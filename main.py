from enum import Enum

from fastapi import FastAPI

app = FastAPI()


class Spice(str, Enum):
    pepper = "pepper"
    salt = "salt"
    maggi = "maggi"


@app.get('/')
async def root():
    return {"message": "Hello World"}


# order is important, prz before {name}
@app.get('/names/name/prz')
async def read_prz():
    return {"Name": "PRZ"}


@app.get('/names/name/{name}')
async def read_name(name: str):
    return {"Name": name, "Type": str(type(name))}


@app.get('/names/age/{age}')
async def read_age(age: int):
    """ Raise 422 Unprocessable Entity if age is not int """
    return {"Age": age, "Type": str(type(age))}


@app.get('/spice/{spice}')
async def get_spice(spice: Spice):
    """ If spice is other than Enum raise 422 """
    if spice is Spice.pepper:
        return {"action": "use pepper"}
    
    if spice.value == "salt":
        return {"action": "use salt"}

    return {"action": "use maggi"}


@app.get('/get-query-params')
async def get_query_parameter(mandatory: str, flag: bool = False, extra: str | None = None):
    """
    ?mandatory=zupa&flag=on&extra=olaboga
    extra: str | None = None -> syntax for python 3.10 and above
    Before python 3.10 extra: Union[str, None] = None
    """
    return {
        'mandatory': mandatory,
        'flag': flag,
        'extra': extra,
    }
