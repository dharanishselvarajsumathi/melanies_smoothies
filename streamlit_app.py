# Import python packages
import streamlit as st
import requests

from snowflake.snowpark.functions import col

# Page configuration
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

# Fetch fruit list from Snowflake
my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
)

# Convert Snowflake table to Python list
fruit_list = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()

# Fruit multiselect
options = st.multiselect(
    "Choose your fruits 🍓 (max 5)",
    fruit_list,
    max_selections=5
)

# If user selected fruits
if options:

    # Create ingredient string
    ingredients_string = ", ".join(options)

    # Show selected ingredients
    st.write("Your smoothie ingredients:", ingredients_string)

    # Loop through selected fruits
    for fruit_chosen in options:

        # Convert fruit name for API compatibility
        fruit_api_name = fruit_chosen.lower().rstrip("s")

        # Section title
        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:

            # API request
            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{fruit_api_name}"
            )

            # Check response success
            if smoothiefroot_response.status_code == 200:

                # Convert API response to JSON
                fruit_data = smoothiefroot_response.json()

                # Show nutrition data
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

# Place order button
if st.button("Place Order"):

    # Validation
    if not name_of_order:
        st.error("Please enter a smoothie name.")

    elif not options:
        st.error("Please choose at least one fruit.")

    else:

        try:

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

        except Exception as e:
            st.error(f"Database Error: {e}")
