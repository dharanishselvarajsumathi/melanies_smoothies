# Import python packages.
import streamlit as st
# Title
st.title(f"Customize Your Smoothie 🥤 {st.__version__}")
st.write("Choose your fruits for your smoothie")


name_of_order = st.text_input("Name of Smoothie")
st.write("The name of the smoothie will be:", name_of_order)


# Fetch data
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Convert to list
fruit_list = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()

# Multiselect
options = st.multiselect(
    "Choose your fruits 🍓 (max 5)",
    fruit_list,
    max_selections=5
)

# Process selection
if options:
    fruit_string = " ".join(options)   # clean conversion
    st.write("Your smoothie ingredients:", fruit_string)

    # Button to place order (important)
    if st.button("Place Order"):
        my_insert_stmt = f"""
    insert into smoothies.public.orders(ingredients, name_on_order)
    values ('{fruit_string}', '{name_of_order}')
"""

        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered! ✅")
