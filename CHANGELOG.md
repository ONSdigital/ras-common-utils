0.0.8 (unreleased)
------------------

- On CloudFoundry, carry out validation checks to ensure all required environment variables are found in the 
environment, throwing an exception to report all missing values.
- Convert to using upper-case for all environment variables.
- Use underscore rather than period as the delimiter in environment variables.


0.0.7 (2017-09-05)
------------------

- Ensure that schema of all tables is correctly adjusted for postgres deployment.


0.0.6 (2017-09-04)
------------------

- Convert feature flag results to boolean.


0.0.5 (2017-08-11)
------------------

- Enable overriding status code in RasError class.


0.0.4 (2017-08-09)
------------------

- Fix issue looking-up dependency values when running on CloudFoundry.


0.0.3 (2017-08-08)
------------------

- Fix to ensure RasCloudFoundryConfig correctly resolves dependencies to VCAP_SERVICES values.


0.0.2 (2017-07-17)
------------------

- Use upper-case names for service variables.
- Add to_json() function to RasError.


0.0.1 (2017-07-12)
------------------