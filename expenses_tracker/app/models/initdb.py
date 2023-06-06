from app.models.categories import Category, SubCategory


def create_categories(database, categories_dict: dict):

    for category_name, sub_categories in categories_dict.items():
        category = Category(name=category_name)
        database.session.add(category)

        for sub_category_name in sub_categories:
            sub_category = SubCategory(
                name=sub_category_name, category=category)
            database.session.add(sub_category)

    database.session.commit()
