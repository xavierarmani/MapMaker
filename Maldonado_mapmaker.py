'''
Author: Xavier Maldonado
Instructor: Dr. Klump
CS 245 – Object-Oriented Programming
April 28, 2016

 This is a database-driven mapping application. Given a set of city names, latitudes, and longitudes stored in a mysql
 database, this application will plot the cities in their proper locations on a Turtle Graphics canvas.
'''

#import mysql.connector
import turtle
from operator import attrgetter


# The Shape superclass for all shapes
class Shape:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, x):
        self.__x = x

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, y):
        self.__y = y

    def calc_area(self):
        pass

    def call_perim(self):
        pass

    def get_shape_type(self):
        return "s"

    def to_string(self):
        return "%s %d %d" % (self.get_shape_type(), self.x, self.y)

    def get_draw_params(self):
        return [self.get_shape_type(), self.x, self.y]


'''
 Banner, a subclass of Shape designed to hold text, which has additional
 member called text implemented as a property. The inherited properties x and y define
 where the starting corner of the text will be located.
'''


class Banner(Shape):
    def __init__(self, x, y, text):
        super().__init__(x, y)
        self.text = text

    def get_shape_type(self):
        return "banner"

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, txt):
        self.__text = (txt)

    def to_string(self):
        return "%s %s" % (super().to_string(), self.text)

    def get_draw_params(self):
        result = super().get_draw_params()
        result.extend([self.text])
        return result


# Location is the model class that stores the name, latitude, and longitude of a location
class Location:
    def __init__(self, lat, long, name):
        self.name = name
        self.lat = lat
        self.long = long

    def to_string(self):
        return "%s %d %d" % (self.name, self.lat, self.long)


'''
 MySql_Database class represents the connection to the database and enables execution of queries against it.
 The "connect" function establishes a connection and the "execute" function performs a query against the data.
 The MySql_Database class also includes a data member called "cursor" that allows interaction with the
 data that was fetched through the most recent query.
'''


class MySql_Database:
    def __init__(self, server_name, database, user, pword):
        self.server = server_name
        self.database = database
        self.user = user
        self.pword = pword
        self.conn = None

    @property
    def server(self):
        return self.__server

    @server.setter
    def server(self, server_name):
        if server_name == "":
            self.__server = "localhost"
        else:
            self.__server = server_name

    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.server,
                database=self.database,
                user=self.user,
                password=self.pword)
        except:
            self.conn = None

    def execute(self, query):
        if self.conn != None:
            cursor = self.conn.cursor()
            cursor.execute(query)
            return cursor
        else:
            return None


'''
 MySql_Map_Data_Fetcher includes a dbase data member that refers to the associated MySql_Database object which
 represents a connection to the database. get_locations function that retrieves Location data from the database
 and returns the locations as a list of Location objects.
'''


class MySql_Map_Data_Fetcher:
    @staticmethod
    def get_locations(server_name, dbase_name, username, password, table_name):

        dbase = MySql_Database(server_name, dbase_name, username, password)
        try:
            dbase.connect()
            results = dbase.execute("select * from %s" % table_name)
            loc_list = []
            if results is not None:
                for (loc_name, loc_lat, loc_long) in results:
                    location = Location(loc_lat, loc_long, loc_name)
                    loc_list.append(location)
            else:
                print("Error - no results from any database")

            dbase.conn.close()
            return loc_list

        except:
            print("Please check for invalid input")
            quit()


'''
Turtle_Map_Controller is a controller class that will draw the locations as Banner objects using Turtle Graphics.
the draw_map function takes in the locations and places them on the map in the correct places.
'''


class Turtle_Draw_Shape_Controller:
    def __init__(self, width, height):
        turtle.setup(width, height)
        self.window = turtle.Screen()
        self.artist = turtle.Turtle()

    def draw_map(self, shapes):
        max_lat_scan = max(shapes, key=attrgetter('x'))
        min_lat_scan = min(shapes, key=attrgetter('x'))
        delta_lat = max_lat_scan.x - min_lat_scan.x

        max_long_scan = max(shapes, key=attrgetter('y'))
        min_long_scan = min(shapes, key=attrgetter('y'))
        delta_long = max_long_scan.y - min_long_scan.y

        for s in shapes:

            self.artist.penup()
            params = s.get_draw_params()  # params[0] is the shapetype
            lat = params[1]
            long = params[2]

            X = (-1 * (long - min_long_scan.y) * 400 / delta_long) + 170
            Y = ((lat - min_lat_scan.x) * 400 / delta_lat) - 200

            self.artist.goto(X, Y)
            self.artist.pendown()

            if (params[0] == "banner"):
                self.artist.write(params[3])

    def close(self):
        self.window.bye()


'''
 The main function prints the heading, gathers information to access a data base,then collects the necessary list of
 Location objects. A list of Banner objects is created from that list of locations. Finally, the map can be drawn once
 the draw_map function has been passed the list of banner objects.
'''


def main():
    print("******************** Map Maker ********************")
    server_name = input("Enter name of database server: ").strip()
    dbase_name = input("Enter the name of the data base: ").strip()
    table_name = input("Enter the name of the table: ").strip()
    username = input("Enter your username: ").strip()
    password = input("Enter your password: ").strip()

    loc_object_list = MySql_Map_Data_Fetcher.get_locations(server_name, dbase_name, username, password, table_name)

    banner_object_list = []
    for i in loc_object_list:
        banner = Banner(i.lat, i.long, i.name)
        banner_object_list.append(banner)

    tdsc = Turtle_Draw_Shape_Controller(500, 500)
    tdsc.draw_map(banner_object_list)

    input("Press enter to continue.")


if __name__ == "__main__":
    main()
