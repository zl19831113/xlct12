# Zujuanwang Deployment Scripts

This directory contains scripts to help deploy the Zujuanwang application to a remote server.

## Server Information
- Server IP: 120.26.12.100
- Username: root
- Target Path: /var/www/zujuanwang

## Available Deployment Methods

### 1. Using rsync (deploy.sh)
The `deploy.sh` script uses rsync for file transfer and handles the server setup. It requires sshpass to be installed for non-interactive password handling.

```bash
./deploy/deploy.sh
```

### 2. Using scp with tar (deploy_scp.sh)
The `deploy_scp.sh` script uses scp and tar for file transfer. It may require manual password entry at different stages of the deployment.

```bash
./deploy/deploy_scp.sh
```

### 3. Using expect (deploy_expect.sh)
The `deploy_expect.sh` script uses the expect command to handle interactive password entry. This requires the expect command to be installed.

```bash
./deploy/deploy_expect.sh
```

### 4. Manual Deployment
If the automated scripts encounter issues, follow the manual deployment guide in `MANUAL_DEPLOYMENT.md`.

## What These Scripts Do

All deployment methods perform the following tasks:

1. Transfer files from your local machine to the server
2. Set up the Python virtual environment
3. Install required Python packages
4. Configure Nginx as a reverse proxy
5. Set up the systemd service for automatic startup
6. Start the application

## After Deployment

After successful deployment, the application should be accessible at:

http://120.26.12.100

## Troubleshooting

If you encounter issues during deployment, refer to the troubleshooting section in the `MANUAL_DEPLOYMENT.md` file.

## Security Note

The scripts contain the server password. For security reasons, make sure to:
- Keep these files private
- Remove or secure them after deployment
- Consider using SSH keys instead of passwords for authentication in production environments 