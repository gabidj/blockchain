pragma solidity '0.8.7';

contract coin_ico {
    // 1000 USD
    // Introducing the max (total) number of Y Coins available for sale
    uint public max_coins = 1000000;

    // conversion rate
    uint public usd_to_coins = 1000;

    // Total number of coins bought by investors
    uint public total_coins_bought = 0;

    // mapping the investor address to its equity in coins & USD
    mapping(address => uint) equity_coins;
    mapping(address => uint) equity_usd;

    // Checking if investor can buy coins
    modifier can_buy_coins(uint usd_invested) {
        require (usd_invested * usd_to_coins > total_coins_bought);
        _;
    }


    // Checking if investor can buy coins
    /*modifier can_sell_coins(uint coins_to_sell) {
        require (equity_coins[investor] >= coins_to_sell);
    }*/

     function equity_in_coins(address investor) external view returns (uint) {
       return equity_coins[investor];
    }

     function equity_in_usd(address investor) external view returns (uint) {
       return equity_usd[investor];
    }

    // buying coins
    function buy_coins(address investor, uint usd_invested) external
    can_buy_coins(usd_invested) {
        uint coins_bought = usd_invested * usd_to_coins;
        equity_coins[investor] += coins_bought;
        equity_usd[investor] = equity_coins[investor] / usd_to_coins;
        total_coins_bought += coins_bought;
    }

    // Selling Hadcoins
    function sell_coins(address investor, uint coins_sold) external
    // can_sell_coins(usd_invested)
    {
        equity_coins[investor] -= coins_sold;
        equity_usd[investor] = equity_coins[investor] / usd_to_coins;
        total_coins_bought -= coins_sold;
    }
}
