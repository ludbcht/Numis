import { motion } from "framer-motion";

export default function CoinCard({ coin, onClick, condition }) {
  return (
    <motion.div
      whileHover={{ y: -8 }}
      transition={{ duration: 0.3 }}
      onClick={onClick}
      className="cursor-pointer group"
      data-testid="coin-card"
    >
      <div className="relative aspect-square rounded-full overflow-hidden shadow-lg group-hover:shadow-xl transition-shadow mb-4">
        <img
          src={coin.image_url}
          alt={coin.description}
          className="w-full h-full object-cover"
          data-testid="coin-image"
        />
        {condition && (
          <div className="absolute top-2 right-2 bg-accent text-white text-xs font-semibold px-2 py-1 rounded-full">
            {condition}
          </div>
        )}
      </div>
      <div className="text-center">
        <h3 className="font-heading font-bold text-lg mb-1" data-testid="coin-title">
          {coin.country} {coin.year}
        </h3>
        <p className="text-sm text-muted-foreground line-clamp-2" data-testid="coin-description">
          {coin.description}
        </p>
        <div className="flex gap-2 justify-center mt-2 text-xs text-muted-foreground">
          <span>FDC: {coin.value_fdc}€</span>
          <span>•</span>
          <span>BU: {coin.value_bu}€</span>
          <span>•</span>
          <span>BE: {coin.value_be}€</span>
        </div>
      </div>
    </motion.div>
  );
}
