import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Coins, LogOut, Search, Filter } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import CoinCard from "@/components/CoinCard";
import CoinDetailDialog from "@/components/CoinDetailDialog";
import { motion } from "framer-motion";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function CatalogPage({ user, onLogout }) {
  const navigate = useNavigate();
  const [coins, setCoins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedCountry, setSelectedCountry] = useState("all");
  const [selectedYear, setSelectedYear] = useState("all");
  const [countries, setCountries] = useState([]);
  const [years, setYears] = useState([]);
  const [selectedCoin, setSelectedCoin] = useState(null);
  const [showDialog, setShowDialog] = useState(false);

  useEffect(() => {
    fetchCountries();
    fetchYears();
  }, []);

  useEffect(() => {
    fetchCoins();
  }, [selectedCountry, selectedYear, search]);

  const fetchCountries = async () => {
    try {
      const response = await axios.get(`${API}/countries`);
      setCountries(response.data);
    } catch (error) {
      console.error("Error fetching countries:", error);
    }
  };

  const fetchYears = async () => {
    try {
      const response = await axios.get(`${API}/years`);
      setYears(response.data);
    } catch (error) {
      console.error("Error fetching years:", error);
    }
  };

  const fetchCoins = async () => {
    setLoading(true);
    try {
      const params = {};
      if (selectedCountry !== "all") params.country = selectedCountry;
      if (selectedYear !== "all") params.year = parseInt(selectedYear);
      if (search) params.search = search;

      const response = await axios.get(`${API}/coins`, { params });
      setCoins(response.data);
    } catch (error) {
      console.error("Error fetching coins:", error);
      toast.error("Erreur lors du chargement des pièces");
    } finally {
      setLoading(false);
    }
  };

  const handleCoinClick = (coin) => {
    setSelectedCoin(coin);
    setShowDialog(true);
  };

  const handleLogout = () => {
    onLogout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-background grain-texture" data-testid="catalog-page">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button onClick={() => navigate("/dashboard")} className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center">
                  <Coins className="w-5 h-5 text-accent" />
                </div>
                <h1 className="text-2xl font-heading font-bold tracking-tight">Numis</h1>
              </button>
            </div>
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                onClick={() => navigate("/dashboard")}
                data-testid="nav-dashboard"
              >
                Dashboard
              </Button>
              <Button
                variant="ghost"
                onClick={() => navigate("/collection")}
                data-testid="nav-collection"
              >
                Ma collection
              </Button>
              <Button variant="ghost" onClick={handleLogout} className="gap-2">
                <LogOut className="w-4 h-4" />
                Déconnexion
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h2 className="text-4xl sm:text-5xl font-heading font-bold tracking-tight leading-none mb-2">
            Catalogue
          </h2>
          <p className="text-lg text-muted-foreground">Toutes les pièces de 2€ commémoratives</p>
        </div>

        {/* Filters */}
        <div className="mb-8 grid grid-cols-1 md:grid-cols-12 gap-4">
          <div className="md:col-span-5 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <Input
              data-testid="search-input"
              placeholder="Rechercher une pièce..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 h-12"
            />
          </div>
          <div className="md:col-span-4">
            <Select value={selectedCountry} onValueChange={setSelectedCountry}>
              <SelectTrigger data-testid="country-filter" className="h-12">
                <SelectValue placeholder="Tous les pays" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous les pays</SelectItem>
                {countries.map((country) => (
                  <SelectItem key={country} value={country}>
                    {country}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="md:col-span-3">
            <Select value={selectedYear} onValueChange={setSelectedYear}>
              <SelectTrigger data-testid="year-filter" className="h-12">
                <SelectValue placeholder="Toutes les années" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Toutes les années</SelectItem>
                {years.map((year) => (
                  <SelectItem key={year} value={year.toString()}>
                    {year}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Coins Grid */}
        {loading ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Chargement des pièces...</p>
          </div>
        ) : coins.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Aucune pièce trouvée</p>
          </div>
        ) : (
          <motion.div
            initial="hidden"
            animate="visible"
            variants={{
              visible: {
                transition: {
                  staggerChildren: 0.05,
                },
              },
            }}
            className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8"
            data-testid="coins-grid"
          >
            {coins.map((coin) => (
              <motion.div
                key={coin.id}
                variants={{
                  hidden: { opacity: 0, y: 20 },
                  visible: { opacity: 1, y: 0 },
                }}
              >
                <CoinCard coin={coin} onClick={() => handleCoinClick(coin)} />
              </motion.div>
            ))}
          </motion.div>
        )}
      </main>

      {/* Coin Detail Dialog */}
      {selectedCoin && (
        <CoinDetailDialog
          coin={selectedCoin}
          user={user}
          open={showDialog}
          onOpenChange={setShowDialog}
          onUpdate={fetchCoins}
        />
      )}
    </div>
  );
}
