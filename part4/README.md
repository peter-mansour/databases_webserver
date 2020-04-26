Peter Mansour (phm2122)  
Zejun Lin (zl2844)  

PostgreSQL Account: phm2122  

### Array Option:

Since a user may have multiple skills, I created a table hasSkills to replace
the original hasSkill table, where each user_id corresponds to an array of skills instead of one. Each user may only have one list of skills, thus user_id is the primary key of the table and it references Person table since the user_id must match that of a user in the database. Users can thus join different projects and complete tasks that require different skills based on their skill set. An owner of a project can look for contributors who have one or more specific skills essential for completing a project. We can also verify that contributor's skills include the skill required for completing a task when assigning the task to contributor. A project owner can also check how close user's skills match those required for the project.

#### Queries:

##### Query 1: Find the contact info of users who can good at C++ and are familiar with windows platform
	SELECT P.first_name, P.last_name, P.email, P.phone_num
	FROM Person P
	INNER JOIN hasSkills H
	ON H.user_id = P.user_id
	WHERE H.skills @> '{"C++", "windows"}';

| first_name | last_name | email                     | phone_num  |
|------------|-----------|---------------------------|------------|
| Clinton    | Haley     | Anika_Predovic@thora.info | 4129355575 |
| Darron     | Muller    | Jackson@guadalupe.me      | 8268633031 |

##### Query 2: Check if a contributor's (user_id = Jayson) skills include skill required for completing task (task_id = 73, proj_id = 18)
	SELECT EXISTS(
		SELECT 1
		FROM Person P
		INNER JOIN Contributor C
		ON P.user_id = C.contrib_id and P.username = 'Jayson'
		INNER JOIN hasSkills H
		ON H.user_id = P.user_id
		WHERE (
			SELECT R.skill_name
			FROM requireSkill R
			WHERE R.task_id = 73 and R.proj_id = 18
		) = ANY(H.skills)
	);

| exists |
|--------|
| t      |

##### Query 3: An owner wants to check how much a user's skill set has in common with skills required for project's tasks i.e. if the user is a good match for the project. The value is a ratio between 0 and 100% where 100% is a perfect match.
	SELECT C.contrib_id, 
	&nbsp;&nbsp;&nbsp;&nbsp;COUNT(CASE WHEN R.skill_name = ANY(H.skills) THEN R.skill_name END)*100/COUNT(*) AS match
	FROM Task T
	INNER JOIN Contributes C
	ON C.proj_id = T.proj_id and T.proj_id = 9 and C.contrib_id = 935
	INNER JOIN requireSkill R
	ON R.task_id = T.task_id and R.proj_id = T.proj_id
	INNER JOIN hasSkills H
	ON H.user_id = C.contrib_id
	GROUP BY C.contrib_id;

| contrib_id | match |
|------------|-------|
| 935        | 19    |

##### To create and populate the Table hasSkills:
	CREATE TABLE hasSkills(
		user_id    NUMERIC(12, 0)    REFERENCES Person,
		skills     TEXT[], 
		PRIMARY KEY(user_id)
	);
	
	INSERT INTO hasSkills values(304, array['C++', 'Java', 'windows']);
	INSERT INTO hasSkills values(214, array['python', 'sql', 'french']);
	INSERT INTO hasSkills values(517, array['aerospace', 'mechanical', 'english']);
	INSERT INTO hasSkills values(193, array['medicine', 'biomedical', 'creative']);
	INSERT INTO hasSkills values(691, array['wireless-communi', 'linux', 'windows']);
	INSERT INTO hasSkills values(314, array['mechanical', 'Java', 'python']);
	INSERT INTO hasSkills values(246, array['windows', 'architecture', 'sql']);
	INSERT INTO hasSkills values(933, array['linux', 'creative', 'C++']);
	INSERT INTO hasSkills values(656, array['english', 'french', 'medicine']);
	INSERT INTO hasSkills values(962, array['biomedical', 'mechanical', 'Java']);
	INSERT INTO hasSkills values(935, array['windows', 'Java', 'sql']);
	INSERT INTO hasSkills values(642, array['medicine', 'aerospace', 'python']);
	INSERT INTO hasSkills values(378, array['wireless-communi', 'windows', 'C++']);
	INSERT INTO hasSkills values(229, array['mechanical', 'architecture', 'python']);
	INSERT INTO hasSkills values(633, array['aerospace', 'creative', 'Java']);

### Trigger Option:

Once a contributor is removed from all assigned tasks in a project, the contributor
should be removed from the project. To do so, we created a trigger that calls a
function clean_projs() when deleting a row in Assigned Table to ensure that if the
total number of tasks assigned to a contributor is 0 for that project, 
then the (contributor, project) pair in the Contributes table is removed to remove
the user from project. 

#### The Trigger is created using:

	CREATE OR REPLACE FUNCTION clean_projs() RETURNS trigger AS $$
	DECLARE task_count INTEGER;
	BEGIN
		SELECT COUNT(A.task_id) INTO task_count
		FROM Assigned A
		WHERE A.proj_id = OLD.proj_id and A.contrib_id = OLD.contrib_id;
		IF (task_count = 0) THEN
			DELETE FROM Contributes C WHERE C.contrib_id = OLD.contrib_id and C.proj_id = OLD.proj_id;
		END IF;
	RETURN OLD;
	END; $$
	LANGUAGE PLPGSQL;

	CREATE TRIGGER chk_contrib_status AFTER DELETE ON Assigned
		FOR EACH ROW EXECUTE PROCEDURE clean_projs();

##### To verify that the trigger is working properly:
	//verify that contributor is a member of project
	select * from contributes where contrib_id = 314 and proj_id = 9;

	//the contributor is assigned to 2 tasks in proj 9
	//remove contributor from one assigned task
	DELETE FROM Assigned A where A.contrib_id = 314 and A.proj_id = 9 and task_id = 1;
	
	//verify that contributor is still a member of project
	select * from contributes where contrib_id = 314 and proj_id = 9;
	
	//remove contributor from 2nd assigned task
	//such that contributor is not assigned tasks from proj 9 anymore
	DELETE FROM Assigned A where A.contrib_id = 314 and A.proj_id = 9 and task_id = 4;
	
	//verify that user is no longer a contributor to proj 9
	//if the trigger worked properly, then the contributor 314 and proj 9
	//pair should be removed from the table 'Contributes'
	//the following query should return an empty table
	select * from contributes where contrib_id = 314 and proj_id = 9;

##### Two Queries:

To evaluate a contributor's performance to decide whether or not to remove
the contributor from the project, A project owner needs to find 
how many tasks are assigned to a contributor and how many of those tasks 
are complete
	
	SELECT A.contrib_id AS Contributor, 
		count(distinct(CASE WHEN T.is_complete = TRUE THEN T.task_id END)) AS complete,
		count(distinct(CASE WHEN T.is_complete = FALSE THEN T.task_id END)) AS incomplete
	FROM Assigned A
	INNER JOIN Task T
	ON T.proj_id = A.proj_id and A.proj_id = 5 and A.contrib_id = 691
	GROUP BY A.contrib_id;
	
| contributor | complete | incomplete |
|-------------|----------|------------|
|	 691 |        2 |          3|

To check if contributors are able to complete tasks on time, a project owner
wants to check if any of a contributor's tasks are overdue and by how many
days. Based on the findings, an owner may decide to un-assign the task from
that contributor and assign it to someone else
	
	SELECT A.contrib_id as Contributor, A.task_id as Task, (CURRENT_DATE - T.deadline) AS days_late
	FROM Assigned A
	INNER JOIN Task T
	ON T.proj_id = A.proj_id and T.proj_id = 9 and A.contrib_id = 642
	WHERE (CURRENT_DATE - T.deadline) > 0;
	
| contributor | task | days_late|
|-------------|------|-----------|
|	 642 |    3 |        43|
|	 642 |    4 |        43|