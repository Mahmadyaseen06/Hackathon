"""
Progress Tracker — fetches real data from:
- GitHub (public API, no auth needed)
- LeetCode (GraphQL public endpoint)
- HackerRank (public profile)
- Codeforces (official public API)

Stores daily snapshots in student profile.
"""

import asyncio
import httpx
import json
from datetime import datetime, timezone
from typing import Optional


async def fetch_github_stats(username: str) -> dict:
    """
    Fetch GitHub stats using the free public GitHub API.
    No authentication needed for public profiles.
    """
    if not username:
        return {"error": "No GitHub username provided"}

    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "PlacementPredictor/3.0"}
    base = "https://api.github.com"

    try:
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            # User profile
            user_res = await client.get(f"{base}/users/{username}")
            if user_res.status_code == 404:
                return {"error": f"GitHub user '{username}' not found"}
            user_res.raise_for_status()
            user = user_res.json()

            # Public repos
            repos_res = await client.get(f"{base}/users/{username}/repos?per_page=100&sort=updated")
            repos = repos_res.json() if repos_res.status_code == 200 else []

            # Events (recent activity fallback)
            events_res = await client.get(f"{base}/users/{username}/events/public?per_page=30")
            events = events_res.json() if events_res.status_code == 200 else []

            # Deep commit analysis across top repos
            top_repos = [r["name"] for r in repos[:5] if not r.get("fork")]
            if not top_repos and repos:
                top_repos = [repos[0]["name"]]

            commit_items = []
            commit_dates = set()
            meaningful_commits = 0

            for rname in top_repos[:3]:
                try:
                    c_res = await client.get(f"{base}/repos/{username}/{rname}/commits?author={username}&per_page=10")
                    if c_res.status_code == 200:
                        raw_c = c_res.json()
                        for c in raw_c:
                            c_obj = c.get("commit", {})
                            msg = c_obj.get("message", "").split("\n")[0].strip()
                            a_date = c_obj.get("author", {}).get("date", "")
                            if a_date:
                                commit_dates.add(a_date[:10])
                            is_good = len(msg) > 10 and not any(w == msg.lower() for w in ["update", "test", "fix", ".", "temp", "changes"])
                            if is_good:
                                meaningful_commits += 1
                            commit_items.append({
                                "repo": rname,
                                "sha": c.get("sha", "")[:7],
                                "message": msg[:100],
                                "date": a_date[:10] if a_date else "",
                                "url": c.get("html_url", ""),
                                "is_meaningful": is_good
                            })
                except Exception:
                    pass

        # Fallback to push events if repo commits endpoint was rate limited
        push_events = [e for e in events if e.get("type") == "PushEvent"]
        event_commits_count = sum(
            len(e.get("payload", {}).get("commits", []))
            for e in push_events[:10]
        )
        total_commits = max(len(commit_items), event_commits_count)

        # Analyze repos
        languages = {}
        total_stars = 0
        recent_repos = []

        for repo in repos[:20]:
            if repo.get("language"):
                languages[repo["language"]] = languages.get(repo["language"], 0) + 1
            total_stars += repo.get("stargazers_count", 0)
            recent_repos.append({
                "name": repo["name"],
                "language": repo.get("language", "Unknown"),
                "stars": repo.get("stargazers_count", 0),
                "updated_at": repo.get("updated_at", "")[:10]
            })

        pr_events = len([e for e in events if e.get("type") == "PullRequestEvent"])
        issue_events = len([e for e in events if e.get("type") == "IssuesEvent"])
        top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]

        commit_quality = round((meaningful_commits / max(1, len(commit_items))) * 100) if commit_items else 70

        return {
            "username": username,
            "profile_url": f"https://github.com/{username}",
            "avatar_url": user.get("avatar_url", ""),
            "public_repos": user.get("public_repos", 0),
            "followers": user.get("followers", 0),
            "following": user.get("following", 0),
            "total_stars": total_stars,
            "top_languages": [{"language": l, "repos": c} for l, c in top_languages],
            "recent_commits_30d": total_commits,
            "recent_commits": commit_items[:10],
            "commit_quality_score": commit_quality,
            "active_days_count": len(commit_dates),
            "recent_prs": pr_events,
            "recent_issues": issue_events,
            "recent_repos": recent_repos[:5],
            "activity_score": min(100, total_commits * 3 + pr_events * 5 + issue_events * 2),
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }

    except httpx.TimeoutException:
        return {"error": "GitHub API timeout"}
    except Exception as e:
        return {"error": str(e)}


async def fetch_leetcode_stats(username: str) -> dict:
    """
    Fetch LeetCode stats using the public GraphQL API.
    No authentication needed for public profiles.
    """
    if not username:
        return {"error": "No LeetCode username provided"}

    query = """
    query getUserProfile($username: String!) {
        matchedUser(username: $username) {
            username
            submitStats: submitStatsGlobal {
                acSubmissionNum {
                    difficulty
                    count
                    submissions
                }
            }
            profile {
                ranking
                reputation
                starRating
            }
        }
        userContestRanking(username: $username) {
            attendedContestsCount
            rating
            globalRanking
            totalParticipants
            topPercentage
        }
    }
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(
                "https://leetcode.com/graphql",
                json={"query": query, "variables": {"username": username}},
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0",
                    "Referer": "https://leetcode.com"
                }
            )
            if res.status_code != 200:
                return {"error": f"LeetCode API returned {res.status_code}"}

            data = res.json()
            user = data.get("data", {}).get("matchedUser")
            if not user:
                return {"error": f"LeetCode user '{username}' not found"}

            stats = user.get("submitStats", {}).get("acSubmissionNum", [])
            solved = {s["difficulty"]: s["count"] for s in stats}
            contest = data.get("data", {}).get("userContestRanking") or {}

            easy = solved.get("Easy", 0)
            medium = solved.get("Medium", 0)
            hard = solved.get("Hard", 0)
            total = easy + medium + hard

            # Activity score: weight hard > medium > easy
            activity_score = min(100, easy * 1 + medium * 3 + hard * 5)

            return {
                "username": username,
                "profile_url": f"https://leetcode.com/{username}",
                "total_solved": total,
                "easy_solved": easy,
                "medium_solved": medium,
                "hard_solved": hard,
                "ranking": user.get("profile", {}).get("ranking", 0),
                "contest_rating": round(contest.get("rating", 0), 1),
                "contests_attended": contest.get("attendedContestsCount", 0),
                "global_ranking": contest.get("globalRanking", 0),
                "top_percentage": round(contest.get("topPercentage", 100), 1),
                "activity_score": activity_score,
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }

    except httpx.TimeoutException:
        return {"error": "LeetCode API timeout"}
    except Exception as e:
        return {"error": str(e)}


async def fetch_codeforces_stats(username: str) -> dict:
    """
    Fetch Codeforces stats using their official public API.
    """
    if not username:
        return {"error": "No Codeforces username provided"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # User info
            info_res = await client.get(
                f"https://codeforces.com/api/user.info?handles={username}"
            )
            if info_res.status_code != 200:
                return {"error": "Codeforces API error"}

            info_data = info_res.json()
            if info_data.get("status") != "OK":
                return {"error": f"Codeforces user '{username}' not found"}

            user = info_data["result"][0]

            # Recent submissions
            subs_res = await client.get(
                f"https://codeforces.com/api/user.status?handle={username}&from=1&count=100"
            )
            subs = subs_res.json().get("result", []) if subs_res.status_code == 200 else []
            accepted = [s for s in subs if s.get("verdict") == "OK"]

            # Rating history
            rating_res = await client.get(
                f"https://codeforces.com/api/user.rating?handle={username}"
            )
            contests = rating_res.json().get("result", []) if rating_res.status_code == 200 else []

            # Recent 30 days
            now_ts = datetime.now(timezone.utc).timestamp()
            recent_accepted = [s for s in accepted if now_ts - s.get("creationTimeSeconds", 0) < 2592000]

            return {
                "username": username,
                "profile_url": f"https://codeforces.com/profile/{username}",
                "rating": user.get("rating", 0),
                "max_rating": user.get("maxRating", 0),
                "rank": user.get("rank", "Unrated"),
                "max_rank": user.get("maxRank", "Unrated"),
                "contests_attended": len(contests),
                "total_accepted": len(accepted),
                "recent_accepted_30d": len(recent_accepted),
                "activity_score": min(100, len(recent_accepted) * 4),
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }

    except httpx.TimeoutException:
        return {"error": "Codeforces API timeout"}
    except Exception as e:
        return {"error": str(e)}


async def fetch_hackerrank_stats(username: str) -> dict:
    """
    Fetch HackerRank profile stats via their public REST API.
    """
    if not username:
        return {"error": "No HackerRank username provided"}

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            res = await client.get(
                f"https://www.hackerrank.com/rest/hackers/{username}/scores_elo",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            if res.status_code == 200:
                scores = res.json()
            else:
                scores = {}

            # Also try badges
            badges_res = await client.get(
                f"https://www.hackerrank.com/rest/hackers/{username}/badges",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            badges = badges_res.json().get("models", []) if badges_res.status_code == 200 else []

        top_badges = [
            {"name": b.get("name", ""), "stars": b.get("stars", 0)}
            for b in sorted(badges, key=lambda x: x.get("stars", 0), reverse=True)[:5]
        ]

        # Activity score based on badges
        badge_score = sum(b.get("stars", 0) for b in badges[:10])
        activity_score = min(100, badge_score * 5)

        return {
            "username": username,
            "profile_url": f"https://www.hackerrank.com/{username}",
            "badges": top_badges,
            "total_badges": len(badges),
            "activity_score": activity_score,
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        return {"error": str(e)}


async def fetch_all_platform_stats(student: dict) -> dict:
    """
    Fetch all platform stats for a student in parallel.
    """
    github_user = student.get("github_username", "")
    leetcode_user = student.get("leetcode_username", "")
    codeforces_user = student.get("codeforces_username", "")
    hackerrank_user = student.get("hackerrank_username", "")

    tasks = []
    platform_names = []

    if github_user:
        tasks.append(fetch_github_stats(github_user))
        platform_names.append("github")

    if leetcode_user:
        tasks.append(fetch_leetcode_stats(leetcode_user))
        platform_names.append("leetcode")

    if codeforces_user:
        tasks.append(fetch_codeforces_stats(codeforces_user))
        platform_names.append("codeforces")

    if hackerrank_user:
        tasks.append(fetch_hackerrank_stats(hackerrank_user))
        platform_names.append("hackerrank")

    if not tasks:
        return {"message": "No platform usernames configured"}

    results = await asyncio.gather(*tasks, return_exceptions=True)

    output = {"fetched_at": datetime.now(timezone.utc).isoformat()}
    for name, result in zip(platform_names, results):
        if isinstance(result, Exception):
            output[name] = {"error": str(result)}
        else:
            output[name] = result

    # Compute aggregate activity score
    scores = [
        v.get("activity_score", 0)
        for v in output.values()
        if isinstance(v, dict) and "activity_score" in v
    ]
    output["aggregate_activity_score"] = round(sum(scores) / len(scores), 1) if scores else 0

    return output
