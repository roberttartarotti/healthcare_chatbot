// MongoDB initialization script
// Creates admin user and healthcare database

// Switch to admin database first to create user
db = db.getSiblingDB('admin');

// Create admin user if it doesn't exist
if (!db.getUser("admin")) {
    db.createUser({
        user: "admin",
        pwd: "password",
        roles: [
            { role: "userAdminAnyDatabase", db: "admin" },
            { role: "readWriteAnyDatabase", db: "admin" },
            { role: "dbAdminAnyDatabase", db: "admin" }
        ]
    });
    print("Admin user created successfully in admin database");
} else {
    print("Admin user already exists in admin database");
}

// Switch to healthcare database
db = db.getSiblingDB('healthcare_db');

// Create healthcare_db specific user
if (!db.getUser("admin")) {
    db.createUser({
        user: "admin",
        pwd: "password",
        roles: [
            { role: "readWrite", db: "healthcare_db" },
            { role: "dbAdmin", db: "healthcare_db" }
        ]
    });
    print("Admin user created successfully in healthcare_db database");
} else {
    print("Admin user already exists in healthcare_db database");
}

// Create collections
db.createCollection('patients');
db.createCollection('lab_results');
db.createCollection('appointments');
db.createCollection('medications');

print("Healthcare database initialized successfully"); 