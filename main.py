from enum import Enum
from typing import Any

from fastapi import Body, Cookie, FastAPI, Header, Path, Query
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI()


class Spice(str, Enum):
    pepper = "pepper"
    salt = "salt"
    maggi = "maggi"


### PATH AND QUERY PARAMETERS


@app.get('/')
async def root():
    return {"message": "Hello World"}


# order is important, prz before {name}
@app.get('/names/name/prz')
async def read_prz(
    some_cookie: str | None = Cookie(default=None),
    user_agent: str | None = Header(default=None),
    x_token: list[str] | None = Header(default=None)  # we can send many X-Token
):
    # we can test cookie using curl
    # curl -X GET "http://127.0.0.1:8000/names/name/prz" -H  "accept: application/json"
    # -H  "Cookie: some_cookie=fbab"
    # interesting fact - curl has own User-Agent
    return {
        "Name": "PRZ",
        "some_cookie": some_cookie,
        "user_agent": user_agent,
        "x_token": x_token
    }


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


### REQUEST BODY + NESTED MODELS


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None,
        title="The description of item",
        max_length=30
    )
    price: float = Field(
        gt=0,
        description="The price must be greater than 0",
        examples={
            "good": 25.6,
            "bad": "some string"
        }
    )
    tax: float | None = Field(example="11.5")
    tags: set[str] = set()
    image: Image | None = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "Bar",
                "price": 22.4,
                "tax": 11.0,
                "tags": ["oho", "boho"],
                "image": {
                    "url": "https://example.com",
                    "name": "example"
                }
            }
        }


class UserOutput(BaseModel):
    username: str
    full_name: str | None = None
    age: int = 0


class User(UserOutput):
    password: str


@app.post(
    '/create-user/',
    response_model=UserOutput,
    #response_model_exclude_unset=True
    response_model_exclude={'age'}
)
async def create_user(user: User) -> Any:
    # response_model has priority over return type, but we can use it
    # response_model_exclude_unset - removes values that were not set in request (it's smart!)
    # similar: response_model_exclude_defaults, response_model_exclude_none
    # response_model_exclude / response_model_include
    return user


@app.post('/items/')
async def create_item(item: Item):
    item.name = f"{item.name} + happy!"
    properties = item.dict()
    properties.update({'brutto': item.price + item.tax})
    return properties


@app.put('/items/{item_id}')
async def update_item(item_id: int, item: Item, user: User, counter: int = Body()):
    # Multi arguments for payload, we need to pass
    # "item": {...}
    # "user": {...}
    # "counter: 6 - please notice Body(), so it is not a query parameter
    return {'item_id': item_id, "item": item, "user": user, "counter": counter}


@app.put('/items/single-model/{item_id}')
async def update_single_model(item_id: int, item: Item = Body(embed=True)):
    # Here we pass only 1 argument for payload but we want to force "main" key
    # Then with embed=True we need to set "main" key -> item here
    item_data = item.dict()
    item_data['brutto'] = item.price + item.tax
    return {'item_id': item_id, "item": item_data}


@app.post('/items/create-images')
async def create_images(images: list[Image]):
    # Body(embed=True) alsow works here
    return {"images": images}


### QUERY PARAMETERS AND STRING VALIDATIONS


@app.get('/items/')
async def items(q: str | None = Query(
    default=None,
    alias="item-query",  # so we can use dash in url param
    title="Query String",
    description="Query string for the items",
    min_length=3,
    max_length=50,
    regex="^fixedquery$",
    deprecated=True,
    include_in_schema=False  # set False to hide parameter from /docs
)):
    results = {"fuu": "bar"}
    if q:
        results['q'] = q
    return results


@app.get('/items-multi-q/')
async def handle_multi_queries(q: list = Query(default=['zupa'])):
    """ /items-multi-q/?q=3&q=90 -> [3, 90] """
    query_items = {'q': q}
    return query_items


### PATH PARAMETERS AND NUMERIC VALIDATIONS


@app.get('/new-path/{item_id}')
async def new_path(
    q: str,  # it is mandatory query parameter, order is not important, we can use also Query here
    item_id: int = Path(title="The ID of the item to get", ge=1, lt=1000)
):
    # ge - greater or equal than
    # gt - greater than
    # le, lt - similar with less

    results = {"item_id": item_id, "q": q}
    return results