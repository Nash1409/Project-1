#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from sqlalchemy import func
from forms import *
import sys


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

show = db.Table('show',
  db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
  db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
)
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    num_upcoming_shows = db.Column(db.Integer)
    venues = db.relationship('Venue', secondary=show,
    backref=db.backref('Artist', lazy=True))
    shows = db.relationship('Show', backref='Venue', lazy=True)
    seeking_talent = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(500))
    
def __repr__(self):
  return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy=True)
    seeking_venue = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(500))

def __repr__(self):
  return f'<Artist {self.id} {self.name}>'

class Show(db.Model):
    __tablename__ = 'Show'

    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), primary_key = True) # venue id 
    venue_name = db.Column(db.String) 
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), primary_key = True)
    artist_name = db.Column(db.String)
    start_time = db.Column(db.DateTime, nullable=False)
    
    
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

#show All venues
@app.route('/venues')
def venues():

  # artists.query.all()
  # query = shows.query.filter(venue_id=venues.id)
  # query.count()
  data = []
  venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
  
  cityState_2 = ''
  cityState_1 = '' 
  for ven in venues:
    num = Show.query.filter(Show.venue_id==ven.id)
    numberofshows = num.count()
    cityState_2 = ven.city +','+ ven.state
    if cityState_1 == '' or cityState_1 != cityState_2:
      cityState_1 = ven.city +','+ ven.state
      data.append({
        "city":ven.city,
        "state":ven.state,
        "venues": [{
          "id": ven.id,
          "name":ven.name,
          "num_upcoming_shows": numberofshows 
        }]
      })
    else:
      print ('else')
      data[len(data) - 1]["venues"].append({
      "id": ven.id,
      "name":ven.name,
      "num_upcoming_shows": numberofshows 
      })
  return render_template('pages/venues.html', areas=data);

# do searching in venues
@app.route('/venues/search', methods=['POST'])
def search_venues():
  venue_search = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%')).all()
  count = 0
  data = []
  for search in venue_search:
    data.append({
        "id":search.id,
        "name":search.name
    })

  response = {
    "count":len(data),
    "data":data, 
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

#show venues with givin  id
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = {}
  upcoming_shows = []
  #today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  venue = Venue.query.get(venue_id)
  #show = Show.query.filter(Show.venue_id==venue_id).all()
  show = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
    ).\
    all()

  past_shows = []
  for s in range(0, len(show)):
    past_shows.append({
    "artist_id": show[s].Artist.id,
    "artist_name": show[s].Artist.name,
    "start_time": show[s].Show.start_time
    })
  #upcomingshow = Show.query.filter(Show.venue_id==venue_id , Show.start_time > today).all()
  upcomingshow = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time > datetime.now()
    ).\
    all()

  for s in range(0, len(upcomingshow)):
     upcoming_shows.append({
     "artist_id": upcomingshow[s].Artist.id,
     "artist_name": upcomingshow[s].Artist.name,
     "start_time": upcomingshow[s].Show.start_time
     })
  # flash(upcoming_shows)
  data['id'] = venue.id
  data['name'] = venue.name
  data['genres'] = venue.genres
  data['address'] = venue.address
  data['city'] = venue.city
  data['state'] = venue.state
  data['phone'] = venue.phone
  data['website'] = venue.website
  data['facebook_link'] = venue.facebook_link
  data['seeking_talent'] = venue.seeking_talent
  data['seeking_description'] = venue.seeking_description
  data['image_link'] = venue.image_link
  data['upcoming_shows_count'] = len(upcoming_shows)
  data['upcoming_shows'] = upcoming_shows
  data['past_shows'] = past_shows
  data['past_shows_count'] = len(past_shows)

  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    name = request.form.get('name', '')
    city = request.form.get('city','')
    state = request.form.get('state','')
    address = request.form.get('address','')
    phone = request.form.get('phone','')
      #genres = request.form.get('genres','')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link','')
    venue = Venue(name=name, city=city,state=state, address=address,phone=phone,genres=genres,facebook_link=facebook_link,website='website',image_link='image_link',num_upcoming_shows= 0, seeking_talent = False,seeking_description="NON")
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    shows = Show.query.filter(Show.venue_id==venue_id).delete()
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue could not be deleted.')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')


# show all Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  artists = Artist.query.all()
 
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  artist_search = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%')).all()
  data = []
  for search in artist_search:
    numberofshows = Show.query.filter(Show.artist_id==search.id).count()
    data.append({
        "id":search.id,
        "name":search.name,
        "num_upcoming_shows": numberofshows
    })

  response = {
    "count":len(data),
    "data":data, 
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = {}
  upcoming_shows = []
  past_shows = []
  artist = Artist.query.get(artist_id)
  show = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
        Show.venue_id == Venue.id,
        Show.artist_id == artist_id,
        Show.start_time < datetime.now()
    ).\
    all()
  for s in range(0,len(show)):
    past_shows.append({
    "venue_id": show[s].Venue.id,
    "venue_name": show[s].Venue.name,
    "start_time": show[s].Show.start_time
    })
  upcomingshow = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
        Show.venue_id == Venue.id,
        Show.artist_id == artist_id,
        Show.start_time > datetime.now()
    ).\
    all()
    #flash(upcomingshow)
    #upcomingshow = Show.query.filter(Show.artist_id==artist_id , Show.start_time > today).all()
  for s in range(0,len(upcomingshow)):
    upcoming_shows.append({
    "venue_id": upcomingshow[s].Venue.id,
    "venue_name": upcomingshow[s].Venue.name,
    "start_time": upcomingshow[s].Show.start_time
  })
  data['id'] = artist.id
  data['name'] = artist.name
  data['genres'] = artist.genres
  data['city'] = artist.city
  data['state'] = artist.state
  data['phone'] = artist.phone
  data['website'] = artist.website
  data['facebook_link'] = artist.facebook_link
  data['seeking_venue'] = artist.seeking_venue
  data['seeking_description'] = artist.seeking_description
  data['image_link'] = artist.image_link
  data['upcoming_shows_count'] = len(upcoming_shows)
  data['upcoming_shows'] = upcoming_shows
  data['past_shows'] = past_shows 
  data['past_shows_count'] = len(past_shows) 

  #flash(data['genres']) # I don't know why it is shown spreatly in html page!!
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update

#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={}
  artistquery = Artist.query.get(artist_id)
  artist['id'] = artistquery.id
  artist['name'] = artistquery.name
  artist['genres'] = artistquery.genres
  artist['city'] = artistquery.city
  artist['state'] = artistquery.state
  artist['phone'] = artistquery.phone
  artist['website'] = artistquery.website
  artist['facebook_link'] = artistquery.facebook_link
  artist['seeking_venue'] = artistquery.seeking_venue
  artist['seeking_description'] = artistquery.seeking_description
  artist['image_link'] = artistquery.image_link
  # flash(artist['name'])
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  # artist = Todo.query.get(artist_id)
  # artist.name = name
  # .... all fields
  # db.session.commit()
  artist = Artist.query.get(artist_id)
  artist.name = request.form['name']
  artist.genres = request.form['genres']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.website = request.form['website']
  artist.facebook_link = request.form['facebook_link']
  artist.seeking_venue = True
  artist.seeking_description = request.form['seeking_description']
  artist.image_link = request.form['image_link']
  db.session.commit()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm(request.form)
  venue={}
  venuequery = Venue.query.get(venue_id)
  venue['id'] = venuequery.id
  venue['name'] = venuequery.name
  venue['genres'] = venuequery.genres
  venue['address'] = venuequery.address
  venue['city'] = venuequery.city
  venue['state'] = venuequery.state
  venue['phone'] = venuequery.phone
  venue['website'] = venuequery.website
  venue['facebook_link'] = venuequery.facebook_link
  venue['seeking_talent'] = venuequery.seeking_talent
  venue['seeking_description'] = venuequery.seeking_description
  venue['image_link'] = venuequery.image_link
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  venue.name = request.form['name']
  venue.genres = request.form['genres']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.address = request.form['address']
  venue.phone = request.form['phone']
  venue.website = request.form['website']
  venue.facebook_link = request.form['facebook_link']
  venue.seeking_talent = True
  venue.seeking_description = request.form['seeking_description']
  venue.image_link = request.form['image_link']
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  try:
    name = request.form.get('name', '')
    city = request.form.get('city','')
    state = request.form.get('state','')
    phone = request.form.get('phone','')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link','')
    artist = Artist(name=name, city=city,state=state,phone=phone,genres=genres,facebook_link=facebook_link,website='website',image_link='image_link',seeking_venue = False,seeking_description="NON")
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
# display all shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows = Show.query.all()

  for show in shows: 
    data.append({
     "venue_id":show.venue_id,
      "venue_name":show.venue_name,
      "artist_id": show.artist_id,
      "artist_name":show.artist_name,
      "start_time":show.start_time
      })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    artist_id = request.form.get('artist_id', '')
    artist_name = Artist.query.get(artist_id).name
    venue_id = request.form.get('venue_id','')
    venue_name = Venue.query.get(venue_id).name
    start_time = request.form.get('start_time','')

    show = Show(artist_id=artist_id, venue_id=venue_id,start_time=start_time,venue_name=venue_name,artist_name=artist_name)
    db.session.add(show)
    db.session.commit()
    flash('Show  was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show  could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
