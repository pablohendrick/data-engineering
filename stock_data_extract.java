import java.util.Objects;

public class FinancialData {

    private String symbol;
    private double price;
    private double dailyVariation;
    private double dividends;
    private double marketCap;
    private double tradingVolume;

    public FinancialData() {
    }

    public FinancialData(String symbol, double price, double dailyVariation, double dividends, double marketCap, double tradingVolume) {
        this.symbol = symbol;
        this.price = price;
        this.dailyVariation = dailyVariation;
        this.dividends = dividends;
        this.marketCap = marketCap;
        this.tradingVolume = tradingVolume;
    }

    // Getters and Setters (omitted for brevity)

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        FinancialData that = (FinancialData) o;
        return Double.compare(that.price, price) == 0 &&
                Double.compare(that.dailyVariation, dailyVariation) == 0 &&
                Double.compare(that.dividends, dividends) == 0 &&
                Double.compare(that.marketCap, marketCap) == 0 &&
                Double.compare(that.tradingVolume, tradingVolume) == 0 &&
                Objects.equals(symbol, that.symbol);
    }

    @Override
    public int hashCode() {
        return Objects.hash(symbol, price, dailyVariation, dividends, marketCap, tradingVolume);
    }

    @Override
    public String toString() {
        return "FinancialData{" +
                "symbol='" + symbol + '\'' +
                ", price=" + price +
                ", dailyVariation=" + dailyVariation +
                ", dividends=" + dividends +
                ", marketCap=" + marketCap +
                ", tradingVolume=" + tradingVolume +
                '}';
    }

    public static class YahooFinanceResponse {

        private Quote quote;

        public Quote getQuote() {
            return quote;
        }

        public void setQuote(Quote quote) {
            this.quote = quote;
        }

        public static class Quote {
            private double regularMarketPrice;
            private double regularMarketChangePercent;
            private DividendsInfo dividendsInfo;
            private MarketCap marketCap;
            private RegularMarketVolume regularMarketVolume;

            // Getters and Setters (omitted for brevity)
        }

        public static class DividendsInfo {
            private DividendsPerShare dividendsPerShare;

            // Getters and Setters (omitted for brevity)
        }

        public static class DividendsPerShare {
            private double raw;

            // Getters and Setters (omitted for brevity)
        }

        public static class MarketCap {
            private double raw;

            // Getters and Setters (omitted for brevity)
        }

        public static class RegularMarketVolume {
            private double raw;

            // Getters and Setters (omitted for brevity)
        }
    }
  }
    import org.springframework.beans.factory.annotation.Value;
    import org.springframework.stereotype.Service;
    import org.springframework.web.client.RestTemplate;

    @Service
    public class YahooFinanceService {

        @Value("${yahoo-finance.api.url}")
        private String yahooFinanceApiUrl;

        private final RestTemplate restTemplate;

        public YahooFinanceService(RestTemplate restTemplate) {
            this.restTemplate = restTemplate;
        }

        public FinancialData getFinancialData(String symbol) {
            String apiUrl = String.format("%s/%s", yahooFinanceApiUrl, symbol);
            YahooFinanceResponse response = restTemplate.getForObject(apiUrl, YahooFinanceResponse.class);

            if (response != null && response.getQuote() != null) {
                YahooFinanceResponse.Quote quote = response.getQuote();
                return new FinancialData(
                        symbol,
                        quote.getRegularMarketPrice(),
                        quote.getRegularMarketChangePercent(),
                        quote.getDividendsInfo().getDividendsPerShare().getRaw(),
                        quote.getMarketCap().getRaw(),
                        quote.getRegularMarketVolume().getRaw()
                );
            }

            return null;
        }
    }

    import org.springframework.http.ResponseEntity;
    import org.springframework.web.bind.annotation.GetMapping;
    import org.springframework.web.bind.annotation.PathVariable;
    import org.springframework.web.bind.annotation.RequestMapping;
    import org.springframework.web.bind.annotation.RestController;

    @RestController
    @RequestMapping("/api/finance")
    public class FinanceController {

        private final YahooFinanceService yahooFinanceService;

        public FinanceController(YahooFinanceService yahooFinanceService) {
            this.yahooFinanceService = yahooFinanceService;
        }

        @GetMapping("/stock/{symbol}")
        public ResponseEntity<FinancialData> getStockQuote(@PathVariable String symbol) {
            FinancialData financialData = yahooFinanceService.getFinancialData(symbol);

            if (financialData != null) {
                return ResponseEntity.ok(financialData);
            } else {
                return ResponseEntity.notFound().build();
            }
        }
    }

    import org.apache.http.client.HttpClient;
    import org.apache.http.impl.client.HttpClients;
    import org.springframework.context.annotation.Bean;
    import org.springframework.context.annotation.Configuration;
    import org.springframework.http.client.ClientHttpRequestFactory;
    import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;
    import org.springframework.web.client.RestTemplate;

    @Configuration
    public class AppConfig {

        @Bean
        public RestTemplate restTemplate() {
            return new RestTemplate(clientHttpRequestFactory());
        }

        private ClientHttpRequestFactory clientHttpRequestFactory() {
            HttpComponentsClientHttpRequestFactory factory = new HttpComponentsClientHttpRequestFactory();
            factory.setReadTimeout(5000);
            factory.setConnectTimeout(5000);
            return factory;
        }
    }

    import org.springframework.boot.SpringApplication;
    import org.springframework.boot.autoconfigure.SpringBootApplication;

    @SpringBootApplication
    public class FinanceDataCollectorApplication {

        public static void main(String[] args) {
            SpringApplication.run(FinanceDataCollectorApplication.class, args);
        }
    }
