import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Coins, LogOut, Trash2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import CoinCard from "@/components/CoinCard";
import { motion } from "framer-motion";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function CollectionPage({ user, onLogout }) {
  const navigate = useNavigate();
  const [collection, setCollection] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteItemId, setDeleteItemId] = useState(null);

  useEffect(() => {
    fetchCollection();
  }, []);

  const fetchCollection = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/collection`, {
        params: { user_id: user.id },
      });
      setCollection(response.data);
    } catch (error) {
      console.error("Error fetching collection:", error);
      toast.error("Erreur lors du chargement de la collection");
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async () => {
    if (!deleteItemId) return;

    try {
      await axios.delete(`${API}/collection/${deleteItemId}`, {
        params: { user_id: user.id },
      });
      toast.success("Pièce retirée de la collection");
      fetchCollection();
    } catch (error) {
      console.error("Error removing coin:", error);
      toast.error("Erreur lors de la suppression");
    } finally {
      setDeleteItemId(null);
    }
  };

  const handleLogout = () => {
    onLogout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-background grain-texture" data-testid="collection-page">
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
                onClick={() => navigate("/catalog")}
                data-testid="nav-catalog"
              >
                Catalogue
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
            Ma collection
          </h2>
          <p className="text-lg text-muted-foreground">
            {collection.length} pièce{collection.length > 1 ? "s" : ""} dans votre collection
          </p>
        </div>

        {/* Collection Grid */}
        {loading ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Chargement de votre collection...</p>
          </div>
        ) : collection.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground mb-4">Votre collection est vide</p>
            <Button onClick={() => navigate("/catalog")} data-testid="go-to-catalog">
              Explorer le catalogue
            </Button>
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
            data-testid="collection-grid"
          >
            {collection.map((item) => (
              <motion.div
                key={item.id}
                variants={{
                  hidden: { opacity: 0, y: 20 },
                  visible: { opacity: 1, y: 0 },
                }}
                className="relative"
              >
                <CoinCard coin={item.coin} condition={item.condition} />
                <Button
                  variant="destructive"
                  size="icon"
                  data-testid={`remove-coin-${item.id}`}
                  className="absolute top-2 right-2 w-8 h-8 rounded-full opacity-0 hover:opacity-100 transition-opacity"
                  onClick={() => setDeleteItemId(item.id)}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </motion.div>
            ))}
          </motion.div>
        )}
      </main>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={!!deleteItemId} onOpenChange={() => setDeleteItemId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirmer la suppression</AlertDialogTitle>
            <AlertDialogDescription>
              Êtes-vous sûr de vouloir retirer cette pièce de votre collection ?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel data-testid="cancel-delete">Annuler</AlertDialogCancel>
            <AlertDialogAction onClick={handleRemove} data-testid="confirm-delete">
              Supprimer
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
