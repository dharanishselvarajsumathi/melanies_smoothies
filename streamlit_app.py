# Import python packages.
import streamlit as st
import requests

from snowflake.snowpark.functions import col

# Page config
st.set_page_config(
    page_title="Smoothie App",
    page_icon="🥤"
)

# Title
st.title("Customize Your Smoothie 🥤")
st.write("Choose your fruits for your smoothie")

# User input
name_of_order = st.text_input("Name of Smoothie")

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit data from Snowflake
my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
)

# Convert Snowflake table to Python list
fruit_list = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()

# Multiselect fruits
options = st.multiselect(
    "Choose your fruits 🍓 (max 5)",
    fruit_list,
    max_selections=5
)

# If fruits selected
if options:

    ingredients_string = ""

    # Loop through each selected fruit
    for fruit_chosen in options:

        ingredients_string += fruit_chosen + " "

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # API request
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}"
        )

        # If fruit exists in API
        if smoothiefroot_response.status_code == 200:

            st.dataframe(
                data=smoothiefroot_response.json(),
                use_container_width=True
            )

        # If fruit not found
        else:
            st.warning(f"{fruit_chosen} not found in Smoothiefroot API")

    # Show ingredient string
    st.write("Your smoothie ingredients:", ingredients_string)

# Place order button
if st.button("Place Order"):

    # Validation
    if not name_of_order:
        st.error("Please enter a smoothie name.")

    elif not options:
        st.error("Please choose at least one fruit.")

    else:

        # Insert query
        insert_sql = """
        INSERT INTO smoothies.public.orders
        (ingredients, name_on_order)
        VALUES (?, ?)
        """

        # Execute insert
        session.sql(
            insert_sql,
            params=[ingredients_string, name_of_order]
        ).collect()

        # Success message
        st.success("Your Smoothie is ordered! ✅")
