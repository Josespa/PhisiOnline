def test_index(client):
    response = client.get("/")
    assert response.status_code == 200

def test_index__method_not_allowed(client): 
    response = client.post('/')
    assert response.status_code == 405

def test_createadmin__useradmin(client):
    response = client.post("/createadmin")
    assert response.status_code == 200

def test_register__user(client):
    response = client.post("/register")
    assert response.status_code == 200

def test_login__user(client):
    response = client.post("/login")
    assert response.status_code == 200

def test_home__noaccess(client):
    #cant access because session
    response = client.get("/home")
    assert response.status_code == 302

def test_profile__noaccess(client):
    #cant access because session
    response = client.get("/profile")
    assert response.status_code == 302

def test_updateprofile__noaccess(client):
    #cant access because session
    response = client.get("/updateprofile")
    assert response.status_code == 302

def test_listusers__noaccess(client):
    #cant access because session
    response = client.get("/listusers")
    assert response.status_code == 302


def test_listappointments__noaccess(client):
    #cant access because session
    response = client.get("/listappointments")
    assert response.status_code == 302

def test_addlanguage__noaccess(client):
    #cant access because session
    response = client.get("/addlanguage")
    assert response.status_code == 302

def test_Extensionexercises__noaccess(client):
    #cant access because session
    response = client.get("/Extensionexercises")
    assert response.status_code == 302

def test_Flexionexercises__noaccess(client):
    #cant access because session
    response = client.get("/Flexionexercises")
    assert response.status_code == 302

def test_exercise__noaccess(client):
    #cant access because session
    response = client.post("/exercise/")
    assert response.status_code == 302

def test_editexercise__noaccess(client):
    #cant access because session
    response = client.post("/editexercise/")
    assert response.status_code == 302

def test_patient__noaccess(client):
    #cant access because session
    response = client.post("/patient/")
    assert response.status_code == 302

def test_physiodetail__noaccess(client):
    #cant access because session
    response = client.post("/physiodetail/")
    assert response.status_code == 302