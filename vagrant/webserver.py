from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

newRestaurantForm = '''<!DOCTYPE html>
                        <html>
                            <body>
                                <title>New Restaurant</title>
                                <h1>Make a New Restaurant</h1>
                                <form method='POST' enctype='multipart/form-data' action = '/restaurants/new'>
                                    <input name="restaurantName" type="text" >
                                    <input type="submit" value="Create">
                                </form>
                            </body>
                        </html>
                    '''

editRestaurantForm = '''<!DOCTYPE html>
                        <html>
                            <body>
                                <title>Edit Restaurant</title>
                                <h1>{}</h1>
                                <form method='POST' enctype='multipart/form-data' action = '/restaurants/{}/edit'>
                                    <input name="newRestaurantName" type="text" >
                                    <input type="submit" value="Rename">
                                </form>
                            </body>
                        </html>
                    '''

deleteRestaurantForm = '''<!DOCTYPE html>
                        <html>
                            <body>
                                <title>Delete Restaurant</title>
                                <h1>Are you sure you want to delete {}</h1>
                                <form method='POST' enctype='multipart/form-data' action = '/restaurants/{}/delete'>
                                    <input type="submit" value="Delete">
                                </form>
                            </body>
                        </html>
                    '''


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = "<!DOCTYPE html>"
                output += "<html>"
                output += "<title>Restaurant Menu</title>"
                output += "<body>"

                restaurants = session.query(Restaurant).all()
                for restaurant in restaurants:
                    output += restaurant.name + "<br>"
                    output += "<a href='/restaurants/" + str(restaurant.id) + "/edit'>Edit</a> <br>"
                    output += "<a href='/restaurants/" + str(restaurant.id) + "/delete'>Delete</a> <br><br>"

                output += "<a href='/restaurants/new'>Make a new restaurant</a>"
                output += "</body></html>"
                self.wfile.write(output)
                return

            elif self.path.endswith("/restaurants/new"):
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(newRestaurantForm)
                    return

            elif self.path.endswith("/edit"):
                    restaurant_id = int(self.path.split('/')[2])
                    oldRestaurantName = session.query(Restaurant).filter_by(id = restaurant_id).one().name

                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(editRestaurantForm.format(oldRestaurantName, restaurant_id))
                    return

            elif self.path.endswith("/delete"):
                    restaurant_id = int(self.path.split('/')[2])
                    restaurant_name = session.query(Restaurant).filter_by(id = restaurant_id).one().name

                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(deleteRestaurantForm.format(restaurant_name, restaurant_id))
                    return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                newRestaurantName = ""
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    newRestaurantName = fields.get('restaurantName')

                newRestaurant = Restaurant(name = newRestaurantName[0])
                session.add(newRestaurant)
                session.commit()

                # Send a 303 back to the restaurants page
                self.send_response(303)  # redirect via GET
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()


            if self.path.endswith("/edit"):
                    restaurant_id = int(self.path.split('/')[2])
                    newRestaurantName = ""
                    ctype, pdict = cgi.parse_header(
                        self.headers.getheader('content-type'))
                    if ctype == 'multipart/form-data':
                        fields = cgi.parse_multipart(self.rfile, pdict)
                        newRestaurantName = fields.get('newRestaurantName')

                    restaurantToEdit = session.query(Restaurant).filter_by(id = restaurant_id).one()
                    restaurantToEdit.name = newRestaurantName[0]
                    session.commit()

                    # Send a 303 back to the restaurants page
                    self.send_response(303)  # redirect via GET
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()


            if self.path.endswith("/delete"):
                    restaurant_id = int(self.path.split('/')[2])

                    restaurantToDelete = session.query(Restaurant).filter_by(id = restaurant_id).one()
                    session.delete(restaurantToDelete)
                    session.commit()

                    # Send a 303 back to the restaurants page
                    self.send_response(303)  # redirect via GET
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

        except Exception, ex:
            print str(ex)
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
