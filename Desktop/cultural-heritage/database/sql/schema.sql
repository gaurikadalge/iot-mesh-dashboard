CREATE TABLE heritage_site (
    site_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(100),
    category VARCHAR(50)
);

CREATE TABLE monument (
    monument_id SERIAL PRIMARY KEY,
    site_id INT REFERENCES heritage_site(site_id),
    name VARCHAR(100),
    era VARCHAR(50)
);

