CPSC 449-02 Project 2

Group: Isabel Silva
       Loai Alfarran

Directory Files: 
	1. README.txt (this file) 
	2. userAPI - holds user api.py service along with clients.sql(located in share folder)
        3. timelineAPI - holds timeline api.py service along with timeline.sql (located in sqlFiles folder)
	
	Both userAPI, timelineAPI have the following files: 
		1. Procfile
		2. bin - which holds the init.sh to create database 
		3. var - when database is created the databse file will go here
		4. etc - api.ini and logging.ini are held here   
		5. share (userAPI only) holds the client.sql file
		6. sqlFiles (timelineAPI only) holds the timeline.sql file

Instructions: 
1. Extract files from silva_alfarran_proj2
2. In terminal open silva_alfarran_proj2/userAPI to access user api service
3. To build client database in the same terminal ( ../userAPI) type:$ bash ./bin/init.sh
4. Once database is built in the same terminal (../userAPI) start foreman by typeing: $ foreman start
5. Now open up a new terminal and make sure your are in the same directory as userAPI
	In this new terminal you can call on user services to; the following examples are 
	based in you are using a terminal to make these calls
	1. create new user, ex:  http POST localhost:5000/users/ userName='name here' email='email' pswd='pswd'
	2. check password of user, ex: http POST localhost:5000/users/isabel/pcheck/ pswd='pswd'
	3. add follower, ex: http POST localhost:5000/users/isabel/follow/ follows='name of user to follow'
	4. remove follower, ex: http DELETE localhost:5000/users/delete/ userName='isabel' follows='name'
	Helper calls: 
	4. display all users: ex: http localhost:5000/users
	5. view users followers: ex: http localhost:5000/users/follows/<username> 
6. Within the same terminal of step 3 after exiting foreman start (crtl-c) go to 
	silva_alfarran_proj2/timelineAPI directory
7. To build timeline database in the same terminal (../timelineAPI) type:$ bash ./bin/init.sh
8. Once database is built (IMPORTANT: make sure client.sql database is also built since timelineAPI uses 
	the client database see step 2-3); within the same terminal (../timelineAPI) type: $ foreman start
5. No in a new terminal where the directory is '../timelineAPI' you can call the following services
	1. get user's recent posts ex: http localhost:5000/timeline/<username>
	2. get all users posts, ex: http localhost:5000/timeline/public 
	3. get posts that user follow, ex: http localhost:5000/timeline/<username>/home
	5. user post  tweet , ex: http POST localhost:5000/timeline/<username>/post/ postText='some text'
	helper calls: 
	6. view all users, ex: http localhost:5000/users

Submission Requirements Description: 
	1. python source code: 
		located in userAPI as api.py and timelineAPI as api.py
	2. Procfile 
		both userAPI and timelineAPI have there own procfile 
	3. sql schema 
		located in userAPI/var as clients.sql and timelineAPI/sqlFiles as timelines.sql
	4. README.TXT (this files) 
	5. Docuemtation of instructions (pdf) no pdf just submited a README.txt (this file) 
	6. no compiled directories or databases
	7. only files mentioned in Directory Files in the ReadMe.txt file are important 
