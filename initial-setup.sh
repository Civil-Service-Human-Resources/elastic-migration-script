pip install -r requirements.txt

echo ""
echo "Existing ElasticSearch repo:"
read -p "URL: " EXISTING_ELASTIC_REPO_ENDPOINT
read -p "Username: " EXISTING_ELASTIC_REPO_USERNAME
read -sp "Password: " EXISTING_ELASTIC_REPO_PASSWORD

echo ""
echo ""

echo "New ElasticSearch repo:"
read -p "URL: " NEW_ELASTIC_REPO_ENDPOINT
read -p "Username: " NEW_ELASTIC_REPO_USERNAME
read -sp "Password: " NEW_ELASTIC_REPO_PASSWORD
echo ""
