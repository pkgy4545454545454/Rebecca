import React, { createContext, useContext, useState, useEffect } from 'react';
import { toast } from 'sonner';

const CartContext = createContext();

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

export const CartProvider = ({ children }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);

  // Load cart from localStorage on mount
  useEffect(() => {
    const savedCart = localStorage.getItem('titelli_cart');
    if (savedCart) {
      try {
        setItems(JSON.parse(savedCart));
      } catch (e) {
        console.error('Error loading cart:', e);
      }
    }
  }, []);

  // Save cart to localStorage on change
  useEffect(() => {
    localStorage.setItem('titelli_cart', JSON.stringify(items));
  }, [items]);

  const addItem = (item, enterprise) => {
    setItems(prevItems => {
      const existingItem = prevItems.find(i => i.id === item.id);
      
      if (existingItem) {
        toast.success('Quantité mise à jour');
        return prevItems.map(i => 
          i.id === item.id 
            ? { ...i, quantity: i.quantity + 1 }
            : i
        );
      }
      
      toast.success('Ajouté au panier');
      return [...prevItems, {
        id: item.id,
        name: item.name,
        price: item.price,
        currency: item.currency || 'CHF',
        type: item.type,
        quantity: 1,
        enterprise_id: enterprise?.id || item.enterprise_id,
        enterprise_name: enterprise?.business_name || item.enterprise_name,
        image: item.images?.[0] || null
      }];
    });
  };

  const removeItem = (itemId) => {
    setItems(prevItems => prevItems.filter(i => i.id !== itemId));
    toast.success('Retiré du panier');
  };

  const updateQuantity = (itemId, quantity) => {
    if (quantity < 1) {
      removeItem(itemId);
      return;
    }
    
    setItems(prevItems => 
      prevItems.map(i => 
        i.id === itemId ? { ...i, quantity } : i
      )
    );
  };

  const clearCart = () => {
    setItems([]);
    localStorage.removeItem('titelli_cart');
  };

  const getItemCount = () => {
    return items.reduce((sum, item) => sum + item.quantity, 0);
  };

  const getTotal = () => {
    return items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  };

  const getItemsByEnterprise = () => {
    const grouped = {};
    items.forEach(item => {
      if (!grouped[item.enterprise_id]) {
        grouped[item.enterprise_id] = {
          enterprise_id: item.enterprise_id,
          enterprise_name: item.enterprise_name,
          items: []
        };
      }
      grouped[item.enterprise_id].items.push(item);
    });
    return Object.values(grouped);
  };

  return (
    <CartContext.Provider value={{
      items,
      loading,
      addItem,
      removeItem,
      updateQuantity,
      clearCart,
      getItemCount,
      getTotal,
      getItemsByEnterprise
    }}>
      {children}
    </CartContext.Provider>
  );
};

export default CartContext;
