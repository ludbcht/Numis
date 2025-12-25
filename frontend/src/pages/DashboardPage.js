import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Coins, LogOut, BookOpen, Library } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import ThemeToggle from "@/components/ThemeToggle";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function DashboardPage({ user, onLogout }) {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/collection/stats`, {
        params: { user_id: user.id },
      });
      setStats(response.data);
    } catch (error) {
      console.error("Error fetching stats:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    onLogout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-background grain-texture" data-testid="dashboard-page">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center">
                <Coins className="w-5 h-5 text-accent" />
              </div>
              <h1 className="text-2xl font-heading font-bold tracking-tight">Numis</h1>
            </div>
            <div className="flex items-center gap-2">
              <ThemeToggle />
              <Button
                variant="ghost"
                onClick={handleLogout}
                data-testid="logout-button"
                className="gap-2"
              >
                <LogOut className="w-4 h-4" />
                Déconnexion
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="mb-8">
            <h2 className="text-4xl sm:text-5xl font-heading font-bold tracking-tight leading-none mb-2">
              Bonjour, {user.username}
            </h2>
            <p className="text-lg text-muted-foreground">Gérez votre collection de pièces de 2€ commémoratives</p>
          </div>

          {/* Stats Grid */}
          {loading ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground">Chargement des statistiques...</p>
            </div>
          ) : stats ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
              <div className="p-6 rounded-2xl bg-secondary/50 border border-border/50" data-testid="total-coins-stat">
                <p className="text-xs uppercase tracking-widest font-semibold text-muted-foreground mb-2">
                  Total de pièces
                </p>
                <p className="text-4xl font-heading font-bold tabular-nums">{stats.total_coins}</p>
              </div>

              <div className="p-6 rounded-2xl bg-secondary/50 border border-border/50" data-testid="owned-coins-stat">
                <p className="text-xs uppercase tracking-widest font-semibold text-muted-foreground mb-2">
                  Pièces possédées
                </p>
                <p className="text-4xl font-heading font-bold tabular-nums">{stats.owned_coins}</p>
              </div>

              <div className="p-6 rounded-2xl bg-secondary/50 border border-border/50" data-testid="completion-stat">
                <p className="text-xs uppercase tracking-widest font-semibold text-muted-foreground mb-2">
                  Complétion
                </p>
                <p className="text-4xl font-heading font-bold tabular-nums">{stats.completion_percentage}%</p>
              </div>

              <div className="p-6 rounded-2xl bg-secondary/50 border border-border/50" data-testid="total-value-stat">
                <p className="text-xs uppercase tracking-widest font-semibold text-muted-foreground mb-2">
                  Valeur totale
                </p>
                <p className="text-4xl font-heading font-bold tabular-nums">{stats.total_value}€</p>
              </div>
            </div>
          ) : null}

          {/* Action Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <button
              onClick={() => navigate("/catalog")}
              data-testid="go-to-catalog-button"
              className="group p-8 rounded-2xl bg-gradient-to-br from-accent/10 to-accent/5 border border-accent/20 hover:border-accent/40 hover:shadow-xl transition-all duration-300 text-left"
            >
              <div className="w-12 h-12 rounded-full bg-accent/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Library className="w-6 h-6 text-accent" />
              </div>
              <h3 className="text-2xl font-heading font-bold mb-2">Catalogue complet</h3>
              <p className="text-muted-foreground">
                Explorez toutes les pièces de 2€ commémoratives disponibles
              </p>
            </button>

            <button
              onClick={() => navigate("/collection")}
              data-testid="go-to-collection-button"
              className="group p-8 rounded-2xl bg-gradient-to-br from-accent/10 to-accent/5 border border-accent/20 hover:border-accent/40 hover:shadow-xl transition-all duration-300 text-left"
            >
              <div className="w-12 h-12 rounded-full bg-accent/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <BookOpen className="w-6 h-6 text-accent" />
              </div>
              <h3 className="text-2xl font-heading font-bold mb-2">Ma collection</h3>
              <p className="text-muted-foreground">
                Consultez et gérez les pièces que vous possédez
              </p>
            </button>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
