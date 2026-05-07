# -----------------------------------
# IMPORT PYTHON PACKAGES
# -----------------------------------

import streamlit as st
import requests

from snowflake.snowpark.functions import col

# -----------------------------------
# PAGE CONFIGURATION
# -----------------------------------

st.set_page_config(
    page_title="Smoothie App",
    page_icon="🥤",
    layout="centered"
)

# -----------------------------------
# PAGE TITLE
# -----------------------------------

st.title("Customize Your Smoothie 🥤")
st.write("Choose your fruits for your smoothie")

# -----------------------------------
# USER INPUT
# -----------------------------------

name_of_order = st.text_input(
    "Name of Smoothie"
)

# -----------------------------------
# SNOWFLAKE CONNECTION
# -----------------------------------

cnx = st.connection("snowflake")

session = cnx.session()

# -----------------------------------
# FETCH DATA FROM SNOWFLAKE
# -----------------------------------

my_dataframe = (
    session.table(
        "smoothies.public.fruit_options"
    )
    .select(
        col("FRUIT_NAME"),
        col("SEARCH_ON")
    )
)

# -----------------------------------
# CONVERT TO PANDAS DATAFRAME
# -----------------------------------

pd_df = my_dataframe.to_pandas()

# -----------------------------------
# CREATE FRUIT LIST
# -----------------------------------

fruit_list = (
    pd_df["FRUIT_NAME"]
    .tolist()
)

# -----------------------------------
# MULTISELECT FRUITS
# -----------------------------------

ingredients_list = st.multiselect(
    "Choose your fruits 🍓 (max 5)",
    fruit_list,
    max_selections=5
)

# -----------------------------------
# IF USER SELECTS FRUITS
# -----------------------------------
if ingredients_list:
    # Build clean ingredients string
    ingredients_string = ", ".join(ingredients_list)
    
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]
        
        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )
        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )
    
    st.write("Your smoothie ingredients:", ingredients_string)
# -----------------------------------
# PLACE ORDER BUTTON
# -----------------------------------

if st.button("Place Order"):
    insert_sql = """
    INSERT INTO smoothies.public.orders
    (
        ingredients,
        name_on_order,
        order_filled,
        order_ts
    )
    VALUES
    (
        ?,
        ?,
        ?,
        CURRENT_TIMESTAMP()
    )
    """
    session.sql(
        insert_sql,
        params=[
            ingredients_string,  # ✅ fixed
            name_of_order,
            False
        ]
    ).collect()
    st.success(
        "Your Smoothie is ordered! ✅"
    )
