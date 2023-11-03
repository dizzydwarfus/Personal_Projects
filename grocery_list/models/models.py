from pydantic import BaseModel
from datetime import datetime
from typing import Union, List


class ProductCard(BaseModel):  # use search_products(query='') method
    webshopId: int  # this is the productId
    hqId: int
    title: str
    salesUnitSize: str
    unitPriceDescription: str
    images: list
    priceBeforeBonus: float
    orderAvailabilityStatus: str
    mainCategory: str
    subCategory: str
    subCategoryId: int
    brand: str
    shopType: str
    availableOnline: bool
    isPreviouslyBought: bool
    descriptionHighlights: str
    propertyIcons: list
    properties: dict
    nix18: bool
    isStapelBonus: bool
    extraDescriptions: list
    isBonus: bool
    descriptionFull: str
    isOrderable: bool
    isInfiniteBonus: bool
    isSample: bool
    isVirtualBundle: bool
    isFavorite: bool
    minBestBeforeDays: int
    discountLabels: list


class ProductDetails(BaseModel):
    webshopId: int  # this is the productId
    hqId: int
    title: str
    salesUnitSize: str
    unitPriceDescription: str
    priceBeforeBonus: float
    orderAvailabilityStatus: str
    mainCategory: str
    subCategory: str
    subCategoryId: int
    brand: str
    shopType: str
    availableOnline: bool
    isPreviouslyBought: bool
    descriptionHighlights: str
    nix18: bool
    isStapelBonus: bool
    isBonus: bool
    descriptionFull: str
    isOrderable: bool
    isInfiniteBonus: bool
    isSample: bool
    isVirtualBundle: bool
    isFavorite: bool
    minBestBeforeDays: int


class ProductPrice(BaseModel):
    priceId: int
    productId: int
    price: float
    date: datetime
    bonusPrice: float


class NutritionalInfo(BaseModel):  # use get_product_details(productId) method
    productId: int
    energyKcal: float  # ENER- / energie
    energyKj: float  # ENER- / energie
    fat: float  # FAT / vet
    saturatedFat: float  # FASAT / waarvan verzadigd
    unsaturatedFat: float  # X_FUNS / waarvan onverzadigd
    carbohydrates: float  # CHOAVL / koolhydraten
    sugars: float  # SUGAR- / waarvan suikers
    dietaryFiber: float  # FIBTG / Voedingsvezel
    protein: float  # PROT / eiwitten
    salt: float  # SALTEQ / zout
    sodium: float
