# Execution Instructions

To run the Ruby script successfully, follow these steps:

1.  Navigate to the ruby directory:
    ```bash
    cd ruby
    ```

2.  Install dependencies (if not already installed):
    ```bash
    bundle install
    ```

3.  Execute the script using `bundle exec` and load environment variables:
    ```bash
    env $(grep -v '^#' ../.env | xargs) bundle exec ruby main.rb
    ```

**Note:** The `bundle exec` prefix is critical because it ensures the local gems in `vendor/bundle` are used. The `env` command loads the API keys from `.env` in the parent directory.
