import { useState } from "react";
import axios from "axios";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Plus } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function CoinDetailDialog({ coin, user, open, onOpenChange, onUpdate }) {
  const [condition, setCondition] = useState("FDC");
  const [adding, setAdding] = useState(false);

  const handleAdd = async () => {
    setAdding(true);
    try {
      await axios.post(
        `${API}/collection/add`,
        {
          coin_id: coin.id,
          condition: condition,
        },
        {
          params: { user_id: user.id },
        }
      );
      toast.success("Pièce ajoutée à votre collection");
      onUpdate();
      onOpenChange(false);
    } catch (error) {
      console.error("Error adding coin:", error);
      if (error.response?.status === 400) {
        toast.error("Cette pièce est déjà dans votre collection");
      } else {
        toast.error("Erreur lors de l'ajout");
      }
    } finally {
      setAdding(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl" data-testid="coin-detail-dialog">
        <DialogHeader>
          <DialogTitle className="text-2xl font-heading font-bold">
            {coin.country} {coin.year}
          </DialogTitle>
          <DialogDescription>{coin.description}</DialogDescription>
        </DialogHeader>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
          <div className="aspect-square rounded-full overflow-hidden shadow-xl">
            <img
              src={coin.image_url}
              alt={coin.description}
              className="w-full h-full object-cover"
            />
          </div>

          <div className="space-y-4">
            <div>
              <h3 className="font-semibold text-sm text-muted-foreground mb-2">Informations</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Pays:</span>
                  <span className="font-medium">{coin.country}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Année:</span>
                  <span className="font-medium">{coin.year}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Tirage:</span>
                  <span className="font-medium">{coin.mintage.toLocaleString()}</span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-sm text-muted-foreground mb-2">Valeurs estimées</h3>
              <div className="space-y-2">
                <div className="flex justify-between items-center p-2 rounded-lg bg-secondary/50">
                  <span className="text-sm font-medium">FDC (Fleur De Coin)</span>
                  <span className="text-lg font-bold tabular-nums">{coin.value_fdc}€</span>
                </div>
                <div className="flex justify-between items-center p-2 rounded-lg bg-secondary/50">
                  <span className="text-sm font-medium">BU (Brillant Universel)</span>
                  <span className="text-lg font-bold tabular-nums">{coin.value_bu}€</span>
                </div>
                <div className="flex justify-between items-center p-2 rounded-lg bg-secondary/50">
                  <span className="text-sm font-medium">BE (Belle Épreuve)</span>
                  <span className="text-lg font-bold tabular-nums">{coin.value_be}€</span>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t">
              <Label htmlFor="condition" className="text-sm font-medium mb-2 block">
                Ajouter à ma collection
              </Label>
              <div className="flex gap-2">
                <Select value={condition} onValueChange={setCondition}>
                  <SelectTrigger id="condition" data-testid="condition-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="FDC">FDC</SelectItem>
                    <SelectItem value="BU">BU</SelectItem>
                    <SelectItem value="BE">BE</SelectItem>
                  </SelectContent>
                </Select>
                <Button
                  onClick={handleAdd}
                  disabled={adding}
                  data-testid="add-to-collection-button"
                  className="gap-2 bg-accent hover:bg-accent/90"
                >
                  <Plus className="w-4 h-4" />
                  {adding ? "Ajout..." : "Ajouter"}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
