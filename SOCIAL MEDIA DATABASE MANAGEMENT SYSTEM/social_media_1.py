from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# MySQL database connection configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "password123",
    "database": "social_media_new"
}

# Create a MySQL connection 
conn = mysql.connector.connect(**db_config)

# Create a cursor to execute SQL queries
cursor = conn.cursor()

# Define database tables
class User:
    def _init_(self, user_id, username, email):
        self.user_id = user_id
        self.username = username
        self.email = email

class Post:
    def _init_(self, post_id, user_id, caption, location):
        self.post_id = post_id
        self.user_id = user_id
        self.caption = caption
        self.location = location

class Follow:
    def _init_(self, follower_id, followee_id):
        self.follower_id = follower_id
        self.followee_id = followee_id
    
@app.route('/')
def login():
    if request.method == 'POST':
    # Process the submitted username here
        username = request.form.get('username')
        if username:
           return redirect(url_for('home1'))
    return render_template('login.html')


@app.route('/home1', methods=['GET', 'POST'])                      
def home():
    if request.method == 'POST':
        username = request.form.get('username')

    #no. of login by per user
    query0="SELECT email,username, login.login_id AS login_number FROM users NATURAL JOIN login WHERE username=%s"
    cursor.execute(query0,(username,))
    loginno=cursor.fetchall()

    # Fetch user details
    query1 = "SELECT user_id, username, profile_photo_url, bio FROM users WHERE username = %s"
    cursor.execute(query1, (username,))
    user_data = cursor.fetchone()
    
    postss = None
    

    #posts          = []
    #ip_addresses=  []
    #bookmarks=  []
    #hashtag_names=  []
    #user_follow=  []
    #follower=  []

    if user_data:
        user_id = user_data[0]
        
        # Fetch post details
        query2 = "SELECT post_id, caption, location FROM post WHERE user_id = %s"
        cursor.execute(query2, (user_id,))
        postss = cursor.fetchall()
        print(postss)
        # Fetch IP address from login table (example, you may need to adjust this)
        query3 = "SELECT ip FROM login WHERE user_id = %s"
        cursor.execute(query3, (user_id,))
        ip_addresses = cursor.fetchall()

        # Fetch bookmarks (example, you may need to adjust this)
        query4 = "SELECT post_id FROM bookmarks WHERE user_id = %s"
        cursor.execute(query4, (user_id,))
        bookmarks = cursor.fetchall()

        # Fetch hashtag names (example, you may need to adjust this)
        query5 = "SELECT hashtag_name FROM hashtags WHERE hashtag_id IN " \
                 "(SELECT hashtag_id FROM hashtag_follow WHERE user_id = %s)"
        cursor.execute(query5, (user_id,))
        hashtag_names = cursor.fetchall()

        # Fetch IP address from login table
        query3 = "SELECT ip FROM login WHERE user_id = %s"
        cursor.execute(query3, (user_id,))
        ip_addresses = cursor.fetchall()

        query6 = "SELECT u1.username AS follower, u2.username AS followee FROM follows AS f INNER JOIN users AS u1 ON f.follower_id = u1.user_id INNER JOIN users AS u2 ON f.followee_id = u2.user_id WHERE u2.username = %s"
        cursor.execute(query6,(username,))
        user_follow=cursor.fetchall()

        ## Followers > 10
        query8="SELECT followee_id, COUNT(follower_id) AS follower_count FROM follows GROUP BY followee_id HAVING follower_count > 10 ORDER BY COUNT(follower_id) DESC LIMIT 15"
        cursor.execute(query8)
        follower=cursor.fetchall()
               
    return render_template('home1.html',loginno=loginno, user_data=user_data, posts=postss, ip_addresses=ip_addresses, bookmarks=bookmarks, hashtag_names=hashtag_names,user_follow=user_follow,follower=follower)

@app.route('/add_comment', methods=['GET', 'POST'])
def add_comment():
        if request.method == 'POST':
            try:
                # Retrieve data from the request
                user_id = request.form.get('user_id')
                post_id = request.form.get('post_id')
                comment_text = request.form.get('comment_text')
                    
                if user_id:
                        # Call the AddComment procedure
                        cursor.callproc("AddComment", (user_id, post_id, comment_text,))
                        conn.commit()  # Commit changes to the database
                        return 'Comment added successfully!'
            except Exception as e:
                return str(e)  # Return error message if an exception occurs
            finally:
                conn.close()  # Close the cursor

        return render_template('add_comment.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username',None)
        profile_photo_url= request.form['profile_photo_url']
        bio=request.form['bio']
        email = request.form['email']
        # Create a new user and add it to the database
        cursor.execute("INSERT INTO users(username, profile_photo_url, bio,email) VALUES(%s,%s,%s,%s)",[username, profile_photo_url, bio,email])
        cursor.fetchall()
        conn.commit()
        conn.close()
        
    return render_template('register.html')

@app.route('/post', methods=['GET', 'POST'])
def display_post():
    if request.method == 'POST':
        user_id=request.form.get('user-id')
    
        # Fetch the post details from the 'post' table
        post_query = "SELECT post_id, caption, location FROM post WHERE user_id = %s"
        cursor.execute(post_query, (user_id,))
        post_data = cursor.fetchone()

        if post_data:
            post_id = post_data[0]

            # Fetch comments related to the post from the 'comments' table
            comment_query = "SELECT comment_text FROM comments WHERE post_id = %s"
            cursor.execute(comment_query, (post_id,))
            comments = [row[0] for row in cursor.fetchall()]

            # Fetch photo URLs related to the post from the 'photos' table
            photo_query = "SELECT photo_url, size FROM photos WHERE post_id = %s"
            cursor.execute(photo_query, (post_id,))
            photos = [(row[0], row[1]) for row in cursor.fetchall()]

            # Fetch video URLs related to the post from the 'videos' table
            video_query = "SELECT video_url, size FROM videos WHERE post_id = %s"
            cursor.execute(video_query, (post_id,))
            videos = [(row[0], row[1]) for row in cursor.fetchall()]

            #Most Likes Posts
            mlp_query="SELECT post_likes.user_id, post_likes.post_id, COUNT(post_likes.post_id) FROM post_likes, post WHERE post.post_id = post_likes.post_id GROUP BY post_likes.user_id, post_likes.post_id ORDER BY COUNT(post_likes.post_id) DESC LIMIT 10"
            cursor.execute(mlp_query)
            mlp=cursor.fetchall()

            return render_template('post.html', user_id=user_id, post_data=post_data, comments=comments, photos=photos, videos=videos,mlp=mlp)

        else:
            print("Error")
            return render_template('post.html',user_id=user_id, post_data=post_data)
    
    return render_template('post.html')
     
@app.route('/hashtag', methods=['GET','POST'])
def proc1():

    proc=None
    #if request.method =='POST':
      #hashtag = request.json.get('hashtag_name')
    proc='''
      CREATE PROCEDURE InsertNewHashtag(
          IN p_hashtag_name VARCHAR(255)
      )
      BEGIN
          DECLARE v_hashtag_id INT;
          -- Check if the hashtag already exists
          SELECT hashtag_id INTO v_hashtag_id FROM hashtags WHERE hashtag_name = p_hashtag_name;
  
          -- If the hashtag doesn't exist, insert it
          IF v_hashtag_id IS NULL THEN
            INSERT INTO hashtags (hashtag_name) VALUES (p_hashtag_name);
            SET v_hashtag_id = LAST_INSERT_ID();
          END IF;
  
          -- You can return the ID of the inserted or existing hashtag if needed
          SELECT v_hashtag_id AS new_hashtag_id;
      END;
      //
      '''
    if request.method == 'POST':
        try:
            hashtag_name = request.json.get('hashtag_name')
            if not hashtag_name:
                return "Error: No hashtag provided", 400
            
            with cursor:
                # Call the stored procedure to insert the hashtag into the database
                cursor.callproc("InsertNewHashtag", (hashtag_name,))
                #cursor.fetchall()
                conn.commit() # Commit the changes to the database 
            return "Hashtag inserted successfully", 200
        except Exception as e:
            return f"Error: {str(e)}", 500
        finally:
            conn.close()

    return render_template('hashtag.html',proc=proc)

@app.route('/hashtag1', methods=['GET', 'POST'])
def hash():
    #Most Followed Hashtag
    hashtag_q1= "SELECT hashtag_name AS 'Hashtags', COUNT(hashtag_follow.hashtag_id) AS 'Total Follows' FROM hashtag_follow, hashtags  WHERE hashtags.hashtag_id = hashtag_follow.hashtag_id GROUP BY hashtag_follow.hashtag_id ORDER BY COUNT(hashtag_follow.hashtag_id) DESC LIMIT 5"
    cursor.execute(hashtag_q1)
    hashtag_most_followed = cursor.fetchall()
    
    #Most Used Hashtags
    hashtag_q2="SELECT hashtag_name AS 'Trending Hashtags', COUNT(post_tags.hashtag_id) AS 'Times Used' FROM hashtags,post_tags WHERE hashtags.hashtag_id = post_tags.hashtag_id GROUP BY post_tags.hashtag_id ORDER BY COUNT(post_tags.hashtag_id) DESC LIMIT 10"
    cursor.execute(hashtag_q2)
    hashtag_most_used = cursor.fetchall()

    return render_template('hashtag1.html', hashtag_most_followed=hashtag_most_followed, hashtag_most_used=hashtag_most_used)



@app.route('/delete_post', methods=['GET','POST','DELETE'])
def delete_post():
    if request.method == 'POST':
        post_id = request.form.get('post_id')  # Get the post_id from the request
        print(post_id)
        # Delete the post with the specified post_id
        cursor.execute("DELETE FROM post WHERE post_id = %s", (post_id,))
        conn.commit()
        
        #conn.commit()
        conn.close()


    return render_template('delete.html')

@app.route('/filtered_posts', methods=['GET', 'POST'])
def filtered_posts():
        if request.method == 'POST':
            location = request.form.get('location')
            query = "SELECT caption FROM post WHERE location = %s"
            cursor.execute(query, (location,))
            filtered_posts = cursor.fetchall()
        
        return render_template('filtered_posts.html',filtered_posts=filtered_posts)


if __name__ == '__main__':
    app.run(debug=True)

# Close the cursor and database connection when the app is shut down
@app.teardown_appcontext
def close_db(e):
    cursor.close()
    conn.close()