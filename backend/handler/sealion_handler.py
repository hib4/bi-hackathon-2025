from backend.utils.sea_lion import ask_sealion

async def getSealionRespond():
    result = await ask_sealion("hello sealion, how many language do you speak?")
    return {
        "data":result
    }