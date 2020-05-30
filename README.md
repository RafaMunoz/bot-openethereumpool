# Telegram Bot - Open Ethereum Pool

If you are using [Open Ethereum Pool](https://github.com/sammy007/open-ethereum-pool), you may want to implement this Telegram Bot to see the statistics of your Pool and your Wallets at all times.

# Get Started

This Bot is mounted on Docker, so implementing it is very easy. You just need to have a database [MongoDB 4.2.6-bionic](https://hub.docker.com/_/mongo) and this container.

It is important that the database with your username and password are previously created before launching the bot.

## Environment variables
A continuación puedes ver las Environment variables necesarias para el funcionamiento de este contenedor.

 - **$TELEGRAM_TOKEN** -> Token to access the HTTP API of your bot. 
 
 - **$URI_MONGODB**	-> Connection URI with your MongoDB database. 
 
> For example: mongodb://user:pass@192.168.1.2/OpenEthereumPool

 - **$URL_POOL** -> URL of your Pool and where the bot will be able to consult the statistics.

## Start the Container

To run this bot using Docker you can use the following command:

    docker run -d \
    -e "TELEGRAM_TOKEN=YOUR-TELEGRAM-TOKEN" \
    -e "URI_MONGODB=YOUR_URI_CONNECT_MONGODB" \
    -e "URL_POOL=URL_FOR_YOUR_POOL" \
    rafa93m/bot-openethereumpool
    
## We host your bot
If you are not very familiar with these systems or do not feel like setting up your own bot, we can host it for you.

In my profile is the email with which you can get in contact, you do not have to pay anything, it is totally **FREE**.
If you want you can make a small donation of what you want to help us maintain the servers.


## Donations

**ETH**: 0xF47FB0A777881545ED7b97B289961e78e97Aa760


