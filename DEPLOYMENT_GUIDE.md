# Deployment Guide for Manga Bot on Railway

## Step 1: Create a Railway Project
1. Go to [Railway](https://railway.app/) and sign in or create an account.
2. Click on "New Project" and select "Deploy from GitHub".
3. Connect your GitHub account and select the repository containing the Manga Bot code.

## Step 2: Configure Environment Variables
1. In the Railway dashboard, navigate to the "Settings" tab of your project.
2. Under "Environment Variables", add the following variables:
   - `API_ID`: Your Telegram API ID
   - `API_HASH`: Your Telegram API Hash
   - `BOT_TOKEN`: Your Telegram Bot Token
   - `MONGO_URI`: Your MongoDB connection string

## Step 3: Deploy the Bot
1. Click on the "Deploy" button in the Railway dashboard.
2. Wait for the deployment process to complete. You can monitor the logs for any errors.

## Step 4: Monitor and Optimize
1. After deployment, monitor the bot's performance through the Railway dashboard.
2. Make adjustments as necessary based on usage and performance metrics.

## Additional Notes
- Ensure that your code is pushed to the GitHub repository before deploying.
- The free Railway plan has these limitations:
  - 500 hours/month of compute time (about 20 days)
  - 1GB RAM
  - Limited CPU resources
  - Sleeps after 5 minutes of inactivity

## Optimizations for Trial Plan
1. Reduce `max_concurrent_transmissions` in `bot.py` (suggest 50 instead of 100)
2. Decrease `workers` count in `bot.py` (suggest 1 instead of 2)
3. Implement a keep-alive solution (choose one):
   - Add a simple web server with ping endpoint
   - Use uptime robot to ping your bot regularly
   - Create a Telegram command that keeps the bot awake
4. Monitor resource usage closely to stay within the limits of 512 MB RAM and 2 vCPUs.
5. Consider using a lightweight database alternative if MongoDB is too resource-intensive.

## Monitoring
- Check Railway dashboard regularly for:
  - Resource usage
  - Uptime
  - Error logs

## Scaling Considerations
- Upgrade to paid plan if you exceed free tier limits
- Implement queue system for downloads during peak times
- Use caching to reduce database load

This guide will help you successfully deploy the Manga Bot on Railway within free plan constraints.
