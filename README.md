# pairs-trading
The concept of pairs trading has been around since the 80s, and the theory suggests that finding two cointegrated assets (thus, forming a 'pair') with mean-reverting spreads offers a trader or investor the ability to capture profits based on this spread.

For example, if asset A and asset B are deemed to be cointegrated, and the spread is stationary, one would do well to calculate a Z-score of the spread and enter polar positions when this score crosses a threshold, such as 2/-2 (with this being 2/-2 standard deviations away from the mean).
This gives us two scenarios:
Long asset A and short asset B (Long on the pair) when the Z-score dips below -2.
Short asset A and long asset B (Short on the pair) when the Z-score crosses above +2.

I have seen this performed numerous times for equity markets but was interested in seeing if such a pattern existed across a handful of major currency pairs. Confusingly, this meant looking for pairs of pairs, for example examining the spread between GBPUSD and EURUSD. For this example, I'm using 180 days worth of hourly candlestick data for some of the major currency crosses. These assets were selected based on their availability within my MetaTrader5 terminal. 

Let's take a look at some of the outputs:

![image](https://user-images.githubusercontent.com/74067072/145688863-e07010c1-ebae-41ee-b3fa-9a10c28a1114.png)

Here, we've got our list of significantly cointegrated pairs. The cointegration test was performed with the statsmodels library, which fosters the augmented Engle-Granger two-step cointegration approach. 

Now, we have to test our pairs for stationarity, and whether or not these pairs exhibit mean-reverting tendencies. To do this, we employ the Augmented Dicky-Fuller (ADF) statistical test, which tests our data for the presence of a unit root. The null hypothesis suggests a unit root, and this is a property of a stochastic process. If our data is stochastic, we can assume that there is no significant and predictable mean reversion, as the data follows a random walk.

Let's take a look at which spreads were stationary:

![image](https://user-images.githubusercontent.com/74067072/145735056-f86f6274-01ae-4148-94d7-043685eae04a.png)

We now have a handful of spreads that show promise. From these results, we can infer that the spreads are stationary, and calculate a z-score. Creating a z-score in essence creates a new normal distribution of spread data points, and from this, we can develop our thesis for pairs trading. In this instance, 2 and -2 standard deviations (sigmas, or σ) are marked on the chart, indicating when one could consider going long (at -2σ) or short (at +2σ).

![image](https://user-images.githubusercontent.com/74067072/145735961-51d4099a-7f5f-4612-bf36-6a612d203ab0.png)

That's essentially all for this script. I have subsequently loaded some of these z-scores into Backtrader and begun to tinker with creating a potential strategy based upon these values, but I think I'll leave that for another time.

