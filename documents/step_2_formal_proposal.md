# **Capstone 1**

## Project Proposal

### 1. What goal will your website be designed to achieve?

> Create playlists for users that can be pushed to their Spotify account based on a setlist from a band's previous show, or as a "prediction" of a future setlist for that band.

### 2. What kind of users will visit your site? In other words, what is the demographic of your users?

> Live music lovers, or even just people who love a band and want to know what kind of setlist they'd play live. The age demographic would probably skew toward 18-35.

### 3. What data do you plan on using? You may not have picked your actual API yet, which is fine, just outline what kind of data you would like it to contain.

> - [setlist.fm API](https://api.setlist.fm/docs/1.0/index.html) - Dates of shows played, setlists, bands
> - [Spotify API](https://developer.spotify.com/documentation/web-api/) - Links to specific songs, account access for the user (if granted authorization from user)
> - [Bandsintown API](https://app.swaggerhub.com/apis-docs/Bandsintown/PublicAPI/3.0.1) - Upcoming Show dates

### 4. In brief, outline your approach to creating your project (knowing that you may not know everything in advance and that these details might change later). Answer questions like the ones below, but feel free to add more information:

### - What does your database schema look like?

> **_Models:_**
>
> **User** - id, username, password, email, spotify username/id (potentially)
> **Band** - id, name
> **UserBand** - user_id, band_id
> **Playlist** - id, name, description
> **Song**- id, name, band_id
> **PlaylistSong** - playlist_id, song_id, band_id
> **Show** - id, date, venue
> **ShowBand** - show_id, band_id

### - What kinds of issues might you run into with your API?

> - Song names not matching between setlist .fm and spotify
> - Artists performing covers
> - Potentially having no setlist information for a given date,
> - Authorization and access to spotify (very specific TOS and requirements - not necessarily an issue, just a large process to meet all requirements correctly)

### - Is there any sensitive information you need to secure?

> User's spotify login access and the data involved (while user is logged in), the user's password for the site, potentially the user's spotify account ID (they would have to give permission to store it according to Spotify's TOS)

### - What functionality will your app include?

> Create a profile
>
> - Choose favorite bands
> - Store which shows you've attended
> - Store playlists you've created
> - Attach your Spotify account

> Create a playlist
>
> - Choose a band, and either a previous show or "predict a setlist"
> - Setlist is generated, choose whether or not to push it to your Spotify account

> Band Details Page
>
> - See past shows for that band
> - See upcoming shows (if any) in the area you set in your profile

### - What will the user flow look like?

> I will upload a full user flow map as the next step of my process within the next day or so, and it will be included in this same repo. After that for the next step I will begin adding wireframes.

### - What features make your site more than CRUD? Do you have any stretch goals?

> 1.  Creating playlists with the songs linked to spotify so you can click the link and have it open in spotify
> 2.  Generating a playlist that the band may play in the future based on their past setlists and researched theory/interview data with musicians/observations behind setlist construction
