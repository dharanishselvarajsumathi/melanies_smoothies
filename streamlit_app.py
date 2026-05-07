# Import python packages
import streamlit as st
import requests

from snowflake.snowpark.functions import col

# -----------------------------------
# PAGE CONFIGURATION
# -----------------------------------

st.set_page_config(
    page_title="Smoothie App",
    page_icon="🥤"
)

# -----------------------------------
# PAGE TITLE
# -----------------------------------

st.title("Customize Your Smoothie 🥤")
st.write("Choose your fruits for your smoothie")

# -----------------------------------
# USER INPUT
# -----------------------------------

name_of_order = st.text_input("Name of Smoothie")

# -----------------------------------
# SNOWFLAKE CONNECTION
# -----------------------------------

cnx = st.connection("snowflake")
session = cnx.session()

# -----------------------------------
# FETCH DATA FROM SNOWFLAKE
# -----------------------------------

# Fetch fruit display names + API search names
my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(
        col("FRUIT_NAME"),
        col("SEARCH_ON")
    )
)

# Convert Snowflake table to pandas dataframe
fruit_df = my_dataframe.to_pandas()

# Convert fruit names into list for multiselect
fruit_list = fruit_df["FRUIT_NAME"].tolist()

# -----------------------------------
# MULTISELECT FRUITS
# -----------------------------------

options = st.multiselect(
    "Choose your fruits 🍓 (max 5)",
    fruit_list,
    max_selections=5
)

# -----------------------------------
# IF USER SELECTS FRUITS
# -----------------------------------

if options:

    # Convert selected fruits into string
    ingredients_string = ", ".join(options)

    # Show selected fruits
    st.write("Your smoothie ingredients:", ingredients_string)

    # Loop through each selected fruit
    for fruit_chosen in options:

        # -----------------------------------
        # GET API SEARCH NAME FROM DATABASE
        # -----------------------------------

        fruit_api_name = fruit_df.loc[
            fruit_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        # -----------------------------------
        # SHOW FRUIT SECTION TITLE
        # -----------------------------------

        st.subheader(
            f"{fruit_chosen} Nutrition Information"
        )

        try:

            # -----------------------------------
            # API REQUEST
            # -----------------------------------

            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{fruit_api_name}"
            )

            # -----------------------------------
            # CHECK API RESPONSE
            # -----------------------------------

            if smoothiefroot_response.status_code == 200:

                # Convert API response to JSON
                fruit_data = smoothiefroot_response.json()

                # Show nutrition information
                st.dataframe(
                    data=fruit_data,
                    use_container_width=True
                )

            else:

                st.warning(
                    f"{fruit_chosen} not found in Smoothiefroot API"
                )

        except Exception as e:

            st.error(f"API Error: {e}")

# -----------------------------------
# PLACE ORDER BUTTON
# -----------------------------------

if st.button("Place Order"):

    # -----------------------------------
    # VALIDATION
    # -----------------------------------

    if not name_of_order:

        st.error("Please enter a smoothie name.")

    elif not options:

        st.error("Please choose at least one fruit.")

    else:

        try:

            # -----------------------------------
            # INSERT ORDER INTO SNOWFLAKE
            # -----------------------------------

            insert_sql = """
            INSERT INTO smoothies.public.orders
            (ingredients, name_on_order)
            VALUES (?, ?)
            """

            # Execute insert query
            session.sql(
                insert_sql,
                params=[ingredients_string, name_of_order]
            ).collect()

            # -----------------------------------
            # SUCCESS MESSAGE
            # -----------------------------------

            st.success("Your Smoothie is ordered! ✅")

        except Exception as e:

            st.error(f"Database Error: {e}")
