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

    ingredients_string = ""

    # -----------------------------------
    # LOOP THROUGH EACH FRUIT
    # -----------------------------------

    for fruit_chosen in ingredients_list:

        # Build ingredient string
        ingredients_string += (
            fruit_chosen + ", "
        )

        # -----------------------------------
        # GET SEARCH VALUE
        # -----------------------------------

        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        # -----------------------------------
        # SHOW SECTION TITLE
        # -----------------------------------

        st.subheader(
            f"{fruit_chosen} Nutrition Information"
        )

        try:

            # -----------------------------------
            # API REQUEST
            # -----------------------------------

            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            )

            # -----------------------------------
            # SUCCESSFUL RESPONSE
            # -----------------------------------

            if smoothiefroot_response.status_code == 200:

                fruit_data = (
                    smoothiefroot_response
                    .json()
                )

                st.dataframe(
                    data=fruit_data,
                    use_container_width=True
                )

            # -----------------------------------
            # API FAILED
            # -----------------------------------

            else:

                st.warning(
                    f"{fruit_chosen} not found in Smoothiefroot API"
                )

        # -----------------------------------
        # REQUEST ERROR
        # -----------------------------------

        except Exception as e:

            st.error(
                f"API Error: {e}"
            )

    # -----------------------------------
    # SHOW FINAL INGREDIENTS
    # -----------------------------------

    st.write(
        "Your smoothie ingredients:",
        ingredients_string[:-2]
    )

# -----------------------------------
# PLACE ORDER BUTTON
# -----------------------------------

if st.button("Place Order"):

    # -----------------------------------
    # VALIDATION
    # -----------------------------------

    if not name_of_order:

        st.error(
            "Please enter a smoothie name."
        )

    elif not ingredients_list:

        st.error(
            "Please choose at least one fruit."
        )

    else:

        try:

            # -----------------------------------
            # INSERT ORDER
            # -----------------------------------

            insert_sql = """
            INSERT INTO smoothies.public.orders
            (
                ingredients,
                name_on_order
            )
            VALUES
            (
                ?,
                ?
            )
            """

            session.sql(
                insert_sql,
                params=[
                    ingredients_string[:-2],
                    name_of_order
                ]
            ).collect()

            # -----------------------------------
            # SUCCESS MESSAGE
            # -----------------------------------

            st.success(
                "Your Smoothie is ordered! ✅"
            )

        # -----------------------------------
        # DATABASE ERROR
        # -----------------------------------

        except Exception as e:

            st.error(
                f"Database Error: {e}"
            )
