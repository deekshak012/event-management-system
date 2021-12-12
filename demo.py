import pandas as pd
import psycopg2
import streamlit as st
from configparser import ConfigParser
import streamlit.components.v1 as components
"## Event Management System"


@st.cache
def get_config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}


@st.cache
def query_db(sql: str):
    # print(f"Running query_db(): {sql}")

    db_info = get_config()

    # Connect to an existing database
    conn = psycopg2.connect(**db_info)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute(sql)

    # Obtain data
    data = cur.fetchall()

    column_names = [desc[0] for desc in cur.description]

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

    df = pd.DataFrame(data=data, columns=column_names)

    return df

@st.cache
def insert_db(sql: str):
    # print(f"Running query_db(): {sql}")

    db_info = get_config()

    # Connect to an existing database
    conn = psycopg2.connect(**db_info)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute(sql)

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

    return df

def displayEvents(name,available,price):
    if name:
        "## Available events"
        col1, col2, col3= st.columns(3)
        with col1:
            st.write("Event")
        with col2:
            st.write("Tickets Available")
        with col3:
            st.write("Ticket Price")
        for i in range(len(name)):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(name[i])
            with col2:
                st.write(available[i])
            with col3:
                st.write(price[i])
        "## Buy tickets"
        dropdownevents = st.selectbox("Choose Event to buy ticket",name)
        
        guest = st.radio("Do you want to take a guest with you?",['Yes','No'])
        gueststaking = False
        if guest == 'Yes':
            gueststaking = True
            guestname = st.text_input("Enter guest name")
            guestemail = st.text_input("Enter guest email")
        buy = st.button("Buy Tickets")
        if buy:
            try:
                geteventId = f"Select e.name, e.eventid, et.ticketid From event e, eventtickets et Where e.eventid = et.eventid And e.name = '{dropdownevents}'"
                eventids = query_db(geteventId)['eventid'].tolist()
                eventid = eventids[0]
                ticketids = query_db(geteventId)['eventid'].tolist()
                ticketid = ticketids[0]
                if gueststaking:
                    insertquery = f"Insert into userticketsbought values({ticketid},1,2);"
                else:
                    insertquery = f"Insert into userticketsbought values({ticketid},1,1);"
                insert_db(insertquery)
                st.success("Tickets successfully bought")
            except:
                st.write("Sorry! Something went wrong, please try again.")

    else:
        st.write("No available events.")


"## Search for Events"
try:
    search_based_on = ["Location","Date","Preferences","Type"]
    search = st.selectbox("Choose a search criteria", search_based_on)
except:
    st.write("Sorry! Something went wrong, please try again.")

if search == "Location":
    locations = query_db("select name from location order by name;")["name"].tolist()
    location_drop_down =  st.selectbox("Choose a location", locations)
    if location_drop_down:
        event_in_location = f"select e.name, etix.noavailable as available, etix.price from event e join location l on e.locationid = l.locationid join eventtickets etix on e.eventid = etix.eventid where l.name='{location_drop_down}' and etix.noavailable>0;"
        try:
            name = query_db(event_in_location)["name"].tolist()
            available = query_db(event_in_location)["available"].tolist()
            price =  query_db(event_in_location)["price"].tolist()
            displayEvents(name,available,price)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )
elif search == "Date":
    date = query_db("select distinct date from event where date >= now() order by date;")["date"].tolist()
    date_drop_down =  st.selectbox("Choose a date", date)
    if date_drop_down:
        event_in_date = f"select e.name, et.noavailable as available,et.price from event e join eventtickets et on e.eventid = et.eventid where e.date='{date_drop_down}'and et.noavailable>0;"
        try:
            name = query_db(event_in_date)["name"].tolist()
            available = query_db(event_in_date)["available"].tolist()
            price =  query_db(event_in_date)["price"].tolist()
            displayEvents(name,available,price)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )
elif search == "Preferences":
    eventTypeOnPreference = query_db("select distinct(et.type) from eventtype et join userpreference up on up.eventtypeid = et.eventtypeid where up.userid = '1';")["type"].tolist()
    pref_drop_down =  st.selectbox("Choose a preferred event type", eventTypeOnPreference)
    if pref_drop_down:
        event_in_pref = f"select e.name, etix.noavailable as available, etix.price from event e join eventtype et on e.eventtypeid = et.eventtypeid join eventtickets etix on e.eventid = etix.eventid where et.type='{pref_drop_down}' and etix.noavailable>0;"
        try:
            name = query_db(event_in_pref)["name"].tolist()
            available = query_db(event_in_pref)["available"].tolist()
            price =  query_db(event_in_pref)["price"].tolist()
            displayEvents(name,available,price)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )
elif search == "Type":
    eventType = query_db("select distinct type from eventtype order by type;")["type"].tolist()
    type_drop_down =  st.selectbox("Choose a type of event", eventType)
    if type_drop_down:
        event_in_type = f"select e.name, etix.noavailable as available, etix.price from event e join eventtype et on e.eventtypeid = et.eventtypeid join eventtickets etix on e.eventid = etix.eventid where et.type='{type_drop_down}' and etix.noavailable>0;"
        try:
            name = query_db(event_in_type)["name"].tolist()
            available = query_db(event_in_type)["available"].tolist()
            price =  query_db(event_in_type)["price"].tolist()
            displayEvents(name,available,price)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )
    
    
"## Read tables"

sql_all_table_names = "SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)';"
try:
    all_table_names = query_db(sql_all_table_names)["relname"].tolist()
    table_name = st.selectbox("Choose a table", all_table_names)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

if table_name:
    f"Display the table"

    sql_table = f"SELECT * FROM {table_name};"
    try:
        df = query_db(sql_table)
        st.dataframe(df)
    except:
        st.write(
            "Sorry! Something went wrong with your query, please try again."
        )

