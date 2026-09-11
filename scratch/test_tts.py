import asyncio
import edge_tts

async def test_tts():
    text = "Hello, this is a test of the text to speech engine."
    voice = "en-US-ChristopherNeural"
    communicate = edge_tts.Communicate(text, voice)
    
    with open("test_output.mp3", "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
    print("Done generating test_output.mp3")

if __name__ == "__main__":
    asyncio.run(test_tts())
