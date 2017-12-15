import java.util.concurrent.ThreadLocalRandom;
import java.util.Hashtable;
import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;

public class Toss {
    static class Team {
        private String name ;
        private Hashtable<String, String> prefs ;

        public Team(String name) {
            this.name = name ;
            this.prefs = new Hashtable<String, String>() ;
        }

        public void setPreference(String key, String value) {
            this.prefs.put(key, value) ;
        }

        public String getName() {
            return this.name ;
        }

        public String getPreference(List<String> conditions) {
            // Hashtable<String, Integer> choices = new Hashtable<String, Integer>() ;
            // int total = conditions.size() ;
            // for (String c: conditions) {
            //     if(choices.containsKey(prefs.get(c))) {
            //         choices.put(prefs.get(c), 1+choices.get(prefs.get(c))) ;
            //     }  else {
            //         choices.put(prefs.get(c), 1) ;
            //     }
            // }
            // // System.out.println("Collected to " + choices) ;
            // ArrayList<String> s = new ArrayList<String>(choices.keySet()) ;
            // int ch = ThreadLocalRandom.current().nextInt(1, 1 + s.size()) ;
            // return s.get(ch-1) ;

            if( (conditions.size() == 2) &&
                (this.prefs.get(conditions.get(0)) == this.prefs.get(conditions.get(1)))
            ) {
                return this.prefs.get(conditions.get(0)) ;
            } else return "bats" ;
        }
    }

    public static void main(String[] args) {
        String weather, type ;
        if(args.length > 0) {
            weather = args[0].toLowerCase() ;
            if(args.length > 1) {
                type = args[1].toLowerCase() ;
            } else {
                type = "day" ;
            }
        } else {
            weather = "clear" ;
            type = "day" ;
        }
        // System.out.println("The weather is " + weather + " and the match is at " + type + ".") ;

        // Initialise the teams
        Team l  = new Team("Lengaburu") ;
        l.setPreference("clear", "bats") ;
        l.setPreference("cloudy", "bowls") ;
        l.setPreference("day", "bats") ;
        l.setPreference("night", "bowls") ;
        Team c  = new Team("Enchai") ;
        c.setPreference("clear", "bowls") ;
        c.setPreference("cloudy", "bats") ;
        c.setPreference("day", "bowls") ;
        c.setPreference("night", "bats") ;

        // Determine toss winner
        int toss = ThreadLocalRandom.current().nextInt(1, 3) ;
        Team winner ;
        if (toss == 1) {
            winner = l ;
        } else {
            winner = c ;
        }
        // System.out.println("Toss(" + toss + ") won by " + winner.getName()) ;
        String choice = winner.getPreference(Arrays.asList(weather, type)) ;
        System.out.println(winner.getName() + " wins toss and " + choice) ;
    }
}
