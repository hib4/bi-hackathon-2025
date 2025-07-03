from utils.ai import askSealion

async def getSealionRespond():
    result = await askSealion("hello sealion, how many language do you speak?")
    return {
        "data":result
    }