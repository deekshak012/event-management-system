import pandas as pd
import psycopg2
import streamlit as st
from configparser import ConfigParser
import streamlit.components.v1 as components
import datetime
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

def displayEvents(name,date,available,price):
    if name:
        "## Available events"
        col1, col2, col3, col4= st.columns(4)
        with col1:
            st.write("Date")
        with col2:
            st.write("Event")
        with col3:
            st.write("Tickets Available")
        with col4:
            st.write("Ticket Price")

        for i in range(len(name)):
            col1, col2, col3,col4 = st.columns(4)
            with col1:
                st.write(date[i])
            with col2:
                st.write(name[i])
            with col3:
                st.write(available[i])
            with col4:
                st.write(price[i])

        "## Buy tickets"
        dropdownevents = st.selectbox("Choose event to buy tickets",name)
        
        guest = st.radio("Do you want to take a guest with you?",['Yes','No'],index=1)
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
                ticketsAlreadyBoughtQuery = f"select ticketid from userticketsbought where ticketid ='{ticketid}' and userid='EMS1'"
                ticketsAlreadyBought = query_db(ticketsAlreadyBoughtQuery)['ticketid'].tolist()
                if len(ticketsAlreadyBought) > 0:
                    st.error('You already bought tickets to this event. Try to register for different event.') 
                else: 
                    if gueststaking:
                        if not guestname and not guestemail:
                            st.error('Enter guest name and email')
                        elif not guestname:
                            st.error('Enter guest name')
                        elif not guestemail:
                            st.error('Enter guest email')
                        else:
                            insertquery = f"Insert into userticketsbought values('{ticketid}','EMS1',2);"
                            getguestidquery = f"select guestid from userguests"
                            guestids = query_db(getguestidquery)['guestid'].tolist()
                            if len(guestids)>0:
                                guestids.sort()
                                newguestid = guestids[-1]+1
                                guestsinsertquery = f"Insert into userguests Values ({newguestid},'EMS1','{guestname}', '{guestemail}',{ticketid})"
                            else:
                                guestsinsertquery = f"Insert into userguests Values (1,'EMS1','{guestname}', '{guestemail}',{ticketid})"
                            updatenoavaialable = f"update eventtickets set noavailable = noavailable-2 where eventid ={eventid};"
                            insert_db(updatenoavaialable)
                            insert_db(guestsinsertquery)
                            insert_db(insertquery)
                            st.success("Tickets successfully bought")
                    else:
                        insertquery = f"Insert into userticketsbought values('{ticketid}','EMS1',1);"
                        updatenoavaialable = f"update eventtickets set noavailable = noavailable-1 where eventid ={eventid};"
                        insert_db(updatenoavaialable)
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
        event_in_location = f"select e.date, e.name, etix.noavailable as available, etix.price from event e join location l on e.locationid = l.locationid join eventtickets etix on e.eventid = etix.eventid where l.name='{location_drop_down}' and etix.noavailable>0 order by e.date;"
        try:
            name = query_db(event_in_location)["name"].tolist()
            date = query_db(event_in_location)["date"].tolist()
            available = query_db(event_in_location)["available"].tolist()
            price =  query_db(event_in_location)["price"].tolist()
            displayEvents(name,date,available,price)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )
        
elif search == "Date":
    date = query_db("select distinct date from event where date >= now() order by date;")["date"].tolist()
    date_drop_down =  st.date_input("Choose a date",min_value = datetime.date.today()-datetime.timedelta(days=1))
    print(date_drop_down)
    print(type(date_drop_down))
    if date_drop_down:
        event_in_date = f"select e.date, e.name, et.noavailable as available,et.price from event e join eventtickets et on e.eventid = et.eventid where e.date='{date_drop_down}'and et.noavailable>0 order by e.date;"
        try:
            name = query_db(event_in_date)["name"].tolist()
            date = query_db(event_in_date)["date"].tolist()
            available = query_db(event_in_date)["available"].tolist()
            price =  query_db(event_in_date)["price"].tolist()
            displayEvents(name,date,available,price)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )
elif search == "Preferences":
    eventTypeOnPreference = query_db("select distinct(et.type) from eventtype et join userpreference up on up.eventtypeid = et.eventtypeid where up.userid = 'EMS1' order by et.type;")["type"].tolist()
    pref_drop_down =  st.selectbox("Choose a preferred event type", eventTypeOnPreference)
    if pref_drop_down:
        event_in_pref = f"select e.date, e.name, etix.noavailable as available, etix.price from event e join eventtype et on e.eventtypeid = et.eventtypeid join eventtickets etix on e.eventid = etix.eventid where et.type='{pref_drop_down}' and etix.noavailable>0 order by e.date;"
        try:
            name = query_db(event_in_pref)["name"].tolist()
            date = query_db(event_in_pref)["date"].tolist()
            available = query_db(event_in_pref)["available"].tolist()
            price =  query_db(event_in_pref)["price"].tolist()
            displayEvents(name,date,available,price)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )
elif search == "Type":
    eventType = query_db("select distinct type from eventtype order by type;")["type"].tolist()
    type_drop_down =  st.selectbox("Choose a type of event", eventType)
    if type_drop_down:
        event_in_type = f"select e.date, e.name, etix.noavailable as available, etix.price from event e join eventtype et on e.eventtypeid = et.eventtypeid join eventtickets etix on e.eventid = etix.eventid where et.type='{type_drop_down}' and etix.noavailable>0 order by e.date;"
        try:
            name = query_db(event_in_type)["name"].tolist()
            date = query_db(event_in_type)["date"].tolist()
            available = query_db(event_in_type)["available"].tolist()
            price =  query_db(event_in_type)["price"].tolist()
            displayEvents(name,date,available,price)
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

