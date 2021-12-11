# pairs-trading
The concept of pairs trading has been around since the 80s, and the theory suggests that finding two cointegrated assets (thus, forming a 'pair') with mean-reverting spreads offers a trader or investor the ability to capture profits based on this spread.

For example, if asset A and asset B are deemed to be cointegrated, and the spread is stationary, one would do well to calculate a Z-score of the spread and enter polar positions when this score crosses a threshhold, such as 2/-2 (with this being 2/-2 standard deviations away from the mean).
This gives us two scenarios:
Long asset A and short asset B (Long on the pair) when the Z-score dips below -2.
Short asset A and long asset B (Short on the pair) when the Z-score crosses above +2.

I have seen this performed numerous times for equity markets but was interested in seeing if such a pattern existed across a handful of major currency pairs. Confusingly, this meant looking for pairs of pairs, for example examining the spread between GBPUSD and EURUSD.

Let's take a look at some of the outputs:

![image](https://user-images.githubusercontent.com/74067072/145688863-e07010c1-ebae-41ee-b3fa-9a10c28a1114.png)

Here, we've got our list of significantly cointegrated pairs. The cointegration test was performed with the statsmodels library, which fosters the augmented Engle-Granger two-step cointegration approach.
