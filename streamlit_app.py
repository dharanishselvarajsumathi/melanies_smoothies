# Import python packages.
import streamlit as st
from snowflake.snowpark.functions import col

# Title
st.title(f"Customize Your Smoothie 🥤 {st.__version__}")
st.write("Choose your fruits for your smoothie")

# User input
name_of_order = st.text_input("Name of Smoothie")

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch data
my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
)

# Convert to list
fruit_list = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()

# Multiselect
options = st.multiselect(
    "Choose your fruits 🍓 (max 5)",
    fruit_list,
    max_selections=5
)

# Show selected fruits
if options:
    fruit_string = ", ".join(options)
    st.write("Your smoothie ingredients:", fruit_string)

# Place order button
if st.button("Place Order"):

    # Validation
    if not name_of_order:
        st.error("Please enter a smoothie name.")
    
    elif not options:
        st.error("Please choose at least one fruit.")
    
    else:
        # Safe insert query
        insert_sql = """
        INSERT INTO smoothies.public.orders
        (ingredients, name_on_order)
        VALUES (?, ?)
        """

        session.sql(
            insert_sql,
            params=[fruit_string, name_of_order]
        ).collect()

        st.success("Your Smoothie is ordered! ✅")
