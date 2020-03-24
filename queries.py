get_projs="SELECT * FROM Project P WHERE P.owner_id='{uid}'"
login_owner="SELECT * FROM Person P INNER JOIN Owner O ON P.user_id = \
O.owner_id WHERE P.username='{unm}' and P.password='{pwd}'"
login_contrib="SELECT P.user_id FROM Person P INNER JOIN Contributor C ON \
P.user_id = C. contrib_id WHERE P.username='{unm}' and P.password='{pwd}'"