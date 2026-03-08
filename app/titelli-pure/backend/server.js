// ============================================
// TITELLI BACKEND - Node.js + Express + MongoDB
// ============================================

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { MongoClient, ObjectId } = require('mongodb');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

const app = express();
const PORT = process.env.PORT || 8001;

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
let db;
const mongoClient = new MongoClient(process.env.MONGO_URL);

async function connectDB() {
    try {
        await mongoClient.connect();
        db = mongoClient.db(process.env.DB_NAME);
        console.log('✅ Connecté à MongoDB');
    } catch (error) {
        console.error('❌ Erreur MongoDB:', error);
        process.exit(1);
    }
}

// ============ CATEGORIES ============
const PRODUCT_CATEGORIES = [
    { id: "courses_alimentaires", name: "Courses alimentaires" },
    { id: "vetements_mode", name: "Vêtements et accessoires de mode" },
    { id: "enfant", name: "Tout pour mon enfant" },
    { id: "soins", name: "Matériel de soins" },
    { id: "maquillage_beaute", name: "Maquillage et beauté" },
    { id: "sport", name: "Matériel de sport" },
    { id: "loisirs", name: "Matériel de loisirs" },
    { id: "voyages", name: "Nécessaire voyages" },
    { id: "electronique", name: "Appareils électroniques" },
    { id: "bureautique", name: "Matériel de bureautique" },
    { id: "electromenager", name: "Appareils électroménager" },
    { id: "ameublement_deco", name: "Ameublement et décoration" },
    { id: "bricolage_jardinage", name: "Bricolage et jardinage" },
    { id: "immobilier", name: "Bien immobilier" },
    { id: "automobiles", name: "Automobiles" },
    { id: "animaux", name: "Matériel animaux" },
    { id: "haute_joaillerie", name: "Haute joaillerie" },
    { id: "montres", name: "Montres" },
];

const SERVICE_CATEGORIES = [
    { id: "restauration", name: "Restauration" },
    { id: "soins_esthetiques", name: "Soins esthétiques" },
    { id: "coiffure_barber", name: "Coiffeur / Barber" },
    { id: "cours_sport", name: "Cours de sport" },
    { id: "activites_loisirs", name: "Activités et Loisirs" },
    { id: "nettoyage", name: "Personnel de nettoyage" },
    { id: "multiservices", name: "Agent multiservices" },
    { id: "garagiste", name: "Garagiste" },
    { id: "plombier", name: "Plombier" },
    { id: "serrurier", name: "Serrurier" },
    { id: "electricien", name: "Électricien" },
    { id: "formation", name: "Formation" },
    { id: "emploi", name: "Emploi" },
    { id: "sante", name: "Professionnel de la santé" },
    { id: "voyages", name: "Agence de voyages" },
    { id: "agent_immobilier", name: "Agent immobilier" },
    { id: "expert_tech", name: "Expert en technologie" },
    { id: "expert_fiscal", name: "Expert fiscal" },
    { id: "expert_juridique", name: "Expert juridique" },
    { id: "construction", name: "Construction" },
    { id: "veterinaire", name: "Vétérinaire" },
];

const SUBSCRIPTION_PLANS = {
    annual: { name: "Abonnement Annuel", price: 250, duration: 12 },
    premium_annual: { name: "Premium Annuel", price: 540, duration: 12 },
    premium_monthly: { name: "Premium Mensuel", price: 45, duration: 1 },
};

// ============ AUTH MIDDLEWARE ============
const authMiddleware = async (req, res, next) => {
    try {
        const authHeader = req.headers.authorization;
        if (!authHeader || !authHeader.startsWith('Bearer ')) {
            return res.status(401).json({ detail: 'Non authentifié' });
        }
        
        const token = authHeader.split(' ')[1];
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        
        const user = await db.collection('users').findOne(
            { id: decoded.user_id },
            { projection: { password: 0, _id: 0 } }
        );
        
        if (!user) {
            return res.status(404).json({ detail: 'Utilisateur non trouvé' });
        }
        
        req.user = user;
        next();
    } catch (error) {
        return res.status(401).json({ detail: 'Token invalide' });
    }
};

// ============ AUTH ROUTES ============
app.post('/api/auth/register', async (req, res) => {
    try {
        const { email, password, first_name, last_name, phone, user_type } = req.body;
        
        const existing = await db.collection('users').findOne({ email });
        if (existing) {
            return res.status(400).json({ detail: 'Email déjà utilisé' });
        }
        
        const hashedPassword = await bcrypt.hash(password, 10);
        const userId = uuidv4();
        
        const user = {
            id: userId,
            email,
            password: hashedPassword,
            first_name,
            last_name,
            phone: phone || null,
            user_type: user_type || 'client',
            cashback_balance: 0,
            is_premium: false,
            is_verified: false,
            is_certified: false,
            is_labeled: false,
            city: 'Lausanne',
            created_at: new Date().toISOString()
        };
        
        await db.collection('users').insertOne(user);
        
        const token = jwt.sign(
            { user_id: userId, user_type: user.user_type },
            process.env.JWT_SECRET,
            { expiresIn: '7d' }
        );
        
        const { password: _, ...userWithoutPassword } = user;
        res.json({ token, user: userWithoutPassword });
    } catch (error) {
        console.error('Register error:', error);
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

app.post('/api/auth/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        
        const user = await db.collection('users').findOne({ email });
        if (!user) {
            return res.status(401).json({ detail: 'Email ou mot de passe incorrect' });
        }
        
        const validPassword = await bcrypt.compare(password, user.password);
        if (!validPassword) {
            return res.status(401).json({ detail: 'Email ou mot de passe incorrect' });
        }
        
        const token = jwt.sign(
            { user_id: user.id, user_type: user.user_type },
            process.env.JWT_SECRET,
            { expiresIn: '7d' }
        );
        
        const { password: _, _id, ...userWithoutPassword } = user;
        res.json({ token, user: userWithoutPassword });
    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

app.get('/api/auth/me', authMiddleware, (req, res) => {
    res.json(req.user);
});

// ============ ENTERPRISE ROUTES ============
app.post('/api/enterprises', authMiddleware, async (req, res) => {
    try {
        if (req.user.user_type !== 'entreprise') {
            return res.status(403).json({ detail: 'Seules les entreprises peuvent créer un profil' });
        }
        
        const existing = await db.collection('enterprises').findOne({ user_id: req.user.id });
        if (existing) {
            return res.status(400).json({ detail: 'Profil déjà existant' });
        }
        
        const enterprise = {
            id: uuidv4(),
            user_id: req.user.id,
            business_name: req.body.business_name,
            slogan: req.body.slogan || null,
            description: req.body.description,
            category: req.body.category,
            address: req.body.address,
            city: 'Lausanne',
            phone: req.body.phone,
            email: req.body.email,
            website: req.body.website || null,
            logo: null,
            cover_image: null,
            photos: [],
            videos: [],
            is_certified: false,
            is_labeled: false,
            is_premium: false,
            rating: 0,
            review_count: 0,
            created_at: new Date().toISOString()
        };
        
        await db.collection('enterprises').insertOne(enterprise);
        const { _id, ...enterpriseWithoutId } = enterprise;
        res.json(enterpriseWithoutId);
    } catch (error) {
        console.error('Create enterprise error:', error);
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

app.get('/api/enterprises', async (req, res) => {
    try {
        const { category, is_certified, is_labeled, is_premium, search, limit = 50, skip = 0 } = req.query;
        
        const query = {};
        if (category) query.category = category;
        if (is_certified === 'true') query.is_certified = true;
        if (is_labeled === 'true') query.is_labeled = true;
        if (is_premium === 'true') query.is_premium = true;
        if (search) {
            query.$or = [
                { business_name: { $regex: search, $options: 'i' } },
                { description: { $regex: search, $options: 'i' } }
            ];
        }
        
        const enterprises = await db.collection('enterprises')
            .find(query, { projection: { _id: 0 } })
            .skip(parseInt(skip))
            .limit(parseInt(limit))
            .toArray();
        
        const total = await db.collection('enterprises').countDocuments(query);
        
        res.json({ enterprises, total });
    } catch (error) {
        console.error('List enterprises error:', error);
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

app.get('/api/enterprises/:id', async (req, res) => {
    try {
        const enterprise = await db.collection('enterprises').findOne(
            { id: req.params.id },
            { projection: { _id: 0 } }
        );
        
        if (!enterprise) {
            return res.status(404).json({ detail: 'Entreprise non trouvée' });
        }
        
        const services = await db.collection('services_products')
            .find({ enterprise_id: req.params.id }, { projection: { _id: 0 } })
            .toArray();
        
        const reviews = await db.collection('reviews')
            .find({ enterprise_id: req.params.id }, { projection: { _id: 0 } })
            .sort({ created_at: -1 })
            .limit(50)
            .toArray();
        
        res.json({ ...enterprise, services, reviews });
    } catch (error) {
        console.error('Get enterprise error:', error);
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

app.put('/api/enterprises/:id', authMiddleware, async (req, res) => {
    try {
        const enterprise = await db.collection('enterprises').findOne({ id: req.params.id });
        
        if (!enterprise) {
            return res.status(404).json({ detail: 'Entreprise non trouvée' });
        }
        
        if (enterprise.user_id !== req.user.id) {
            return res.status(403).json({ detail: 'Non autorisé' });
        }
        
        const { id, user_id, created_at, _id, ...updateData } = req.body;
        
        await db.collection('enterprises').updateOne(
            { id: req.params.id },
            { $set: updateData }
        );
        
        res.json({ message: 'Profil mis à jour' });
    } catch (error) {
        console.error('Update enterprise error:', error);
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

// ============ SERVICES/PRODUCTS ROUTES ============
app.post('/api/services-products', authMiddleware, async (req, res) => {
    try {
        const enterprise = await db.collection('enterprises').findOne({ user_id: req.user.id });
        
        if (!enterprise) {
            return res.status(404).json({ detail: 'Créez d\'abord un profil entreprise' });
        }
        
        const item = {
            id: uuidv4(),
            enterprise_id: enterprise.id,
            name: req.body.name,
            description: req.body.description,
            price: parseFloat(req.body.price),
            currency: 'CHF',
            category: req.body.category,
            type: req.body.type || 'service',
            images: req.body.images || [],
            is_available: true,
            is_premium: false,
            is_delivery: req.body.is_delivery || false,
            created_at: new Date().toISOString()
        };
        
        await db.collection('services_products').insertOne(item);
        const { _id, ...itemWithoutId } = item;
        res.json(itemWithoutId);
    } catch (error) {
        console.error('Create service/product error:', error);
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

app.get('/api/services-products', async (req, res) => {
    try {
        const { type, category, enterprise_id, limit = 50, skip = 0 } = req.query;
        
        const query = { is_available: true };
        if (type) query.type = type;
        if (category) query.category = category;
        if (enterprise_id) query.enterprise_id = enterprise_id;
        
        const items = await db.collection('services_products')
            .find(query, { projection: { _id: 0 } })
            .skip(parseInt(skip))
            .limit(parseInt(limit))
            .toArray();
        
        const total = await db.collection('services_products').countDocuments(query);
        
        res.json({ items, total });
    } catch (error) {
        console.error('List services/products error:', error);
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

app.delete('/api/services-products/:id', authMiddleware, async (req, res) => {
    try {
        const item = await db.collection('services_products').findOne({ id: req.params.id });
        
        if (!item) {
            return res.status(404).json({ detail: 'Non trouvé' });
        }
        
        const enterprise = await db.collection('enterprises').findOne({ id: item.enterprise_id });
        
        if (enterprise.user_id !== req.user.id) {
            return res.status(403).json({ detail: 'Non autorisé' });
        }
        
        await db.collection('services_products').deleteOne({ id: req.params.id });
        res.json({ message: 'Supprimé' });
    } catch (error) {
        console.error('Delete service/product error:', error);
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

// ============ REVIEWS ROUTES ============
app.post('/api/reviews', authMiddleware, async (req, res) => {
    try {
        const { enterprise_id, rating, comment } = req.body;
        
        const enterprise = await db.collection('enterprises').findOne({ id: enterprise_id });
        if (!enterprise) {
            return res.status(404).json({ detail: 'Entreprise non trouvée' });
        }
        
        const review = {
            id: uuidv4(),
            enterprise_id,
            user_id: req.user.id,
            user_name: `${req.user.first_name} ${req.user.last_name}`,
            rating: parseInt(rating),
            comment,
            created_at: new Date().toISOString()
        };
        
        await db.collection('reviews').insertOne(review);
        
        // Update enterprise rating
        const allReviews = await db.collection('reviews')
            .find({ enterprise_id })
            .toArray();
        
        const avgRating = allReviews.reduce((sum, r) => sum + r.rating, 0) / allReviews.length;
        
        await db.collection('enterprises').updateOne(
            { id: enterprise_id },
            { $set: { rating: Math.round(avgRating * 10) / 10, review_count: allReviews.length } }
        );
        
        const { _id, ...reviewWithoutId } = review;
        res.json(reviewWithoutId);
    } catch (error) {
        console.error('Create review error:', error);
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

app.get('/api/reviews/:enterprise_id', async (req, res) => {
    try {
        const reviews = await db.collection('reviews')
            .find({ enterprise_id: req.params.enterprise_id }, { projection: { _id: 0 } })
            .sort({ created_at: -1 })
            .limit(50)
            .toArray();
        
        res.json(reviews);
    } catch (error) {
        console.error('Get reviews error:', error);
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

// ============ ORDERS ROUTES ============
app.post('/api/orders', authMiddleware, async (req, res) => {
    try {
        const { enterprise_id, items, delivery_address, notes } = req.body;
        
        const total = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        
        const order = {
            id: uuidv4(),
            user_id: req.user.id,
            enterprise_id,
            items,
            total,
            status: 'pending',
            payment_status: 'pending',
            delivery_address: delivery_address || null,
            notes: notes || null,
            created_at: new Date().toISOString()
        };
        
        await db.collection('orders').insertOne(order);
        const { _id, ...orderWithoutId } = order;
        res.json(orderWithoutId);
    } catch (error) {
        console.error('Create order error:', error);
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

app.get('/api/orders', authMiddleware, async (req, res) => {
    try {
        let query;
        
        if (req.user.user_type === 'entreprise') {
            const enterprise = await db.collection('enterprises').findOne({ user_id: req.user.id });
            query = enterprise ? { enterprise_id: enterprise.id } : { user_id: 'none' };
        } else {
            query = { user_id: req.user.id };
        }
        
        const orders = await db.collection('orders')
            .find(query, { projection: { _id: 0 } })
            .sort({ created_at: -1 })
            .limit(100)
            .toArray();
        
        res.json(orders);
    } catch (error) {
        console.error('Get orders error:', error);
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

// ============ PAYMENT ROUTES ============
app.post('/api/payments/checkout', authMiddleware, async (req, res) => {
    try {
        const { package_type, amount } = req.query;
        
        let finalAmount, productName;
        
        if (SUBSCRIPTION_PLANS[package_type]) {
            finalAmount = SUBSCRIPTION_PLANS[package_type].price;
            productName = SUBSCRIPTION_PLANS[package_type].name;
        } else if (package_type === 'order' && amount) {
            finalAmount = parseFloat(amount);
            productName = 'Commande Titelli';
        } else {
            return res.status(400).json({ detail: 'Type de package invalide' });
        }
        
        const origin = req.headers.origin || 'http://localhost:3000';
        
        const session = await stripe.checkout.sessions.create({
            payment_method_types: ['card'],
            line_items: [{
                price_data: {
                    currency: 'chf',
                    product_data: { name: productName },
                    unit_amount: Math.round(finalAmount * 100),
                },
                quantity: 1,
            }],
            mode: 'payment',
            success_url: `${origin}/payment-success.html?session_id={CHECKOUT_SESSION_ID}`,
            cancel_url: `${origin}/payment-cancel.html`,
            metadata: {
                user_id: req.user.id,
                package_type
            }
        });
        
        await db.collection('payment_transactions').insertOne({
            id: uuidv4(),
            session_id: session.id,
            user_id: req.user.id,
            amount: finalAmount,
            currency: 'CHF',
            type: package_type,
            payment_status: 'pending',
            created_at: new Date().toISOString()
        });
        
        res.json({ url: session.url, session_id: session.id });
    } catch (error) {
        console.error('Checkout error:', error);
        res.status(500).json({ detail: error.message });
    }
});

app.get('/api/payments/status/:session_id', async (req, res) => {
    try {
        const session = await stripe.checkout.sessions.retrieve(req.params.session_id);
        
        const paymentStatus = session.payment_status === 'paid' ? 'paid' : 'pending';
        
        await db.collection('payment_transactions').updateOne(
            { session_id: req.params.session_id },
            { $set: { payment_status: paymentStatus } }
        );
        
        if (paymentStatus === 'paid') {
            const transaction = await db.collection('payment_transactions').findOne({ session_id: req.params.session_id });
            if (transaction && transaction.type.includes('premium')) {
                await db.collection('users').updateOne(
                    { id: transaction.user_id },
                    { $set: { is_premium: true, is_verified: true } }
                );
            }
        }
        
        res.json({
            status: session.status,
            payment_status: session.payment_status,
            amount_total: session.amount_total,
            currency: session.currency
        });
    } catch (error) {
        console.error('Payment status error:', error);
        res.status(500).json({ detail: error.message });
    }
});

// ============ CATEGORIES ROUTES ============
app.get('/api/categories/products', (req, res) => {
    res.json(PRODUCT_CATEGORIES);
});

app.get('/api/categories/services', (req, res) => {
    res.json(SERVICE_CATEGORIES);
});

// ============ FEATURED ROUTES ============
app.get('/api/featured/tendances', async (req, res) => {
    try {
        const enterprises = await db.collection('enterprises')
            .find({ is_labeled: true }, { projection: { _id: 0 } })
            .sort({ rating: -1 })
            .limit(6)
            .toArray();
        res.json(enterprises);
    } catch (error) {
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

app.get('/api/featured/guests', async (req, res) => {
    try {
        const enterprises = await db.collection('enterprises')
            .find({ is_certified: true }, { projection: { _id: 0 } })
            .sort({ rating: -1 })
            .limit(6)
            .toArray();
        res.json(enterprises);
    } catch (error) {
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

app.get('/api/featured/offres', async (req, res) => {
    try {
        const items = await db.collection('services_products')
            .find({ is_available: true }, { projection: { _id: 0 } })
            .sort({ created_at: -1 })
            .limit(6)
            .toArray();
        res.json(items);
    } catch (error) {
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

app.get('/api/featured/premium', async (req, res) => {
    try {
        const enterprises = await db.collection('enterprises')
            .find({ is_premium: true }, { projection: { _id: 0 } })
            .sort({ rating: -1 })
            .limit(6)
            .toArray();
        res.json(enterprises);
    } catch (error) {
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

// ============ ADMIN ROUTES ============
app.get('/api/admin/stats', authMiddleware, async (req, res) => {
    try {
        if (req.user.email !== 'admin@titelli.com') {
            return res.status(403).json({ detail: 'Admin uniquement' });
        }
        
        const [total_users, total_enterprises, total_orders, total_reviews] = await Promise.all([
            db.collection('users').countDocuments(),
            db.collection('enterprises').countDocuments(),
            db.collection('orders').countDocuments(),
            db.collection('reviews').countDocuments()
        ]);
        
        const recent_users = await db.collection('users')
            .find({}, { projection: { password: 0, _id: 0 } })
            .sort({ created_at: -1 })
            .limit(10)
            .toArray();
        
        const recent_orders = await db.collection('orders')
            .find({}, { projection: { _id: 0 } })
            .sort({ created_at: -1 })
            .limit(10)
            .toArray();
        
        res.json({
            stats: { total_users, total_enterprises, total_orders, total_reviews },
            recent_users,
            recent_orders
        });
    } catch (error) {
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

app.get('/api/admin/users', authMiddleware, async (req, res) => {
    try {
        if (req.user.email !== 'admin@titelli.com') {
            return res.status(403).json({ detail: 'Admin uniquement' });
        }
        
        const users = await db.collection('users')
            .find({}, { projection: { password: 0, _id: 0 } })
            .limit(100)
            .toArray();
        
        const total = await db.collection('users').countDocuments();
        
        res.json({ users, total });
    } catch (error) {
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

app.put('/api/admin/users/:user_id/verify', authMiddleware, async (req, res) => {
    try {
        if (req.user.email !== 'admin@titelli.com') {
            return res.status(403).json({ detail: 'Admin uniquement' });
        }
        
        const { is_certified, is_labeled } = req.query;
        
        const updateData = { is_verified: true };
        if (is_certified === 'true') updateData.is_certified = true;
        if (is_labeled === 'true') updateData.is_labeled = true;
        
        await db.collection('users').updateOne(
            { id: req.params.user_id },
            { $set: updateData }
        );
        
        await db.collection('enterprises').updateOne(
            { user_id: req.params.user_id },
            { $set: { is_certified: is_certified === 'true', is_labeled: is_labeled === 'true' } }
        );
        
        res.json({ message: 'Utilisateur vérifié' });
    } catch (error) {
        res.status(500).json({ detail: 'Erreur serveur' });
    }
});

// ============ CASHBACK ============
app.get('/api/cashback/balance', authMiddleware, (req, res) => {
    res.json({ balance: req.user.cashback_balance || 0 });
});

// ============ ROOT & HEALTH ============
app.get('/api', (req, res) => {
    res.json({ message: 'Bienvenue sur l\'API Titelli', version: '1.0.0' });
});

app.get('/api/health', (req, res) => {
    res.json({ status: 'healthy' });
});

app.get('/', (req, res) => {
    res.json({ message: 'API Titelli - Allez sur /api ou /api/health' });
});

// ============ START SERVER ============
connectDB().then(() => {
    app.listen(PORT, () => {
        console.log(`🚀 Serveur Titelli démarré sur http://localhost:${PORT}`);
        console.log(`📚 API disponible sur http://localhost:${PORT}/api`);
    });
});
