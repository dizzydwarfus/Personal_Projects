from pydantic import BaseModel
from datetime import datetime
from typing import Union, List, Optional


class ProductCard(BaseModel):  # use search_products(query='') method
    webshopId: int  # this is the productId
    hqId: int
    title: Optional[str] = None
    salesUnitSize: Optional[str] = None
    unitPriceDescription: Optional[str] = None
    images: Optional[list] = None
    priceBeforeBonus: Optional[float] = None
    orderAvailabilityStatus: str
    mainCategory: Optional[str] = None
    subCategory: Optional[str] = None
    subCategoryId: int
    brand: Optional[str] = None
    shopType: Optional[str] = None
    availableOnline: Optional[bool] = None
    isPreviouslyBought: Optional[bool] = None
    descriptionHighlights: Optional[str] = None
    propertyIcons: Optional[list] = None
    properties: Optional[dict] = None
    nix18: Optional[bool] = None
    isStapelBonus: Optional[bool] = None
    extraDescriptions: Optional[list] = None
    isBonus: Optional[bool] = None
    descriptionFull: Optional[str] = None
    isOrderable: Optional[bool] = None
    isInfiniteBonus: Optional[bool] = None
    isSample: Optional[bool] = None
    isVirtualBundle: Optional[bool] = None
    isFavorite: Optional[bool] = None
    minBestBeforeDays: Optional[int] = None
    discountLabels: Optional[list] = None


class ProductDetails(BaseModel):
    webshopId: int  # this is the productId
    hqId: int
    title: Optional[str] = None
    salesUnitSize: Optional[str] = None
    unitPriceDescription: Optional[str] = None
    priceBeforeBonus: Optional[float] = None
    orderAvailabilityStatus: Optional[str] = None
    mainCategory: Optional[str] = None
    subCategory: Optional[str] = None
    subCategoryId: int
    brand: Optional[str] = None
    shopType: Optional[str] = None
    availableOnline: Optional[bool] = None
    isPreviouslyBought: Optional[bool] = None
    descriptionHighlights: Optional[str] = None
    nix18: Optional[bool] = None
    isStapelBonus: Optional[bool] = None
    isBonus: Optional[bool] = None
    descriptionFull: Optional[str] = None
    isOrderable: Optional[bool] = None
    isInfiniteBonus: Optional[bool] = None
    isSample: Optional[bool] = None
    isVirtualBundle: Optional[bool] = None
    isFavorite: Optional[bool] = None
    minBestBeforeDays: Optional[int] = None


class ProductPrice(BaseModel):
    priceId: int
    productId: int
    price: float
    date: datetime
    bonusPrice: float


class NutritionalInfo(BaseModel):  # use get_product_details(productId) method
    productId: int
    nutrientType: str
    nutrientValue: float
    unit: str
    unitLabel: str
