// ============================================
// TITELLI - Script de création de données démo
// ============================================

require('dotenv').config();
const { MongoClient } = require('mongodb');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');

const MONGO_URL = process.env.MONGO_URL;
const DB_NAME = process.env.DB_NAME;

async function seedDatabase() {
    const client = new MongoClient(MONGO_URL);
    
    try {
        await client.connect();
        const db = client.db(DB_NAME);
        console.log('✅ Connecté à MongoDB');

        // Clear existing data (optional)
        console.log('🗑️ Nettoyage des données existantes...');
        await db.collection('users').deleteMany({});
        await db.collection('enterprises').deleteMany({});
        await db.collection('services_products').deleteMany({});
        await db.collection('reviews').deleteMany({});
        await db.collection('orders').deleteMany({});

        // Create admin user
        console.log('👤 Création de l\'admin...');
        const adminPassword = await bcrypt.hash('Admin123!', 10);
        const adminId = uuidv4();
        await db.collection('users').insertOne({
            id: adminId,
            email: 'admin@titelli.com',
            password: adminPassword,
            first_name: 'Admin',
            last_name: 'Titelli',
            phone: '+41 21 000 00 00',
            user_type: 'admin',
            cashback_balance: 0,
            is_premium: true,
            is_verified: true,
            is_certified: true,
            is_labeled: true,
            city: 'Lausanne',
            created_at: new Date().toISOString()
        });

        // Create test client
        console.log('👤 Création du client test...');
        const clientPassword = await bcrypt.hash('Test123!', 10);
        const clientId = uuidv4();
        await db.collection('users').insertOne({
            id: clientId,
            email: 'test@example.com',
            password: clientPassword,
            first_name: 'Marie',
            last_name: 'Dupont',
            phone: '+41 79 123 45 67',
            user_type: 'client',
            cashback_balance: 25.50,
            is_premium: false,
            is_verified: true,
            is_certified: false,
            is_labeled: false,
            city: 'Lausanne',
            created_at: new Date().toISOString()
        });

        // Create enterprise users and their profiles
        console.log('🏢 Création des entreprises démo...');
        
        const enterprises = [
            {
                user: {
                    email: 'spa.luxury@titelli.com',
                    password: 'Demo123!',
                    first_name: 'Sophie',
                    last_name: 'Martin'
                },
                enterprise: {
                    business_name: 'Spa Luxury Lausanne',
                    slogan: 'Votre oasis de bien-être',
                    description: 'Spa haut de gamme offrant des soins de beauté et de relaxation. Massages, soins du visage, manucure et pédicure dans un cadre luxueux et apaisant.',
                    category: 'soins_esthetiques',
                    address: 'Rue du Grand-Pont 12',
                    phone: '+41 21 312 45 67',
                    email: 'contact@spaluxury.ch',
                    website: 'https://www.spaluxury.ch',
                    is_certified: true,
                    is_labeled: true,
                    is_premium: true,
                    rating: 4.8,
                    review_count: 24
                },
                services: [
                    { name: 'Massage relaxant 60min', description: 'Massage complet du corps pour une relaxation profonde', price: 120, type: 'service' },
                    { name: 'Soin visage premium', description: 'Soin complet du visage avec produits bio', price: 95, type: 'service' },
                    { name: 'Manucure & Pédicure', description: 'Soins des mains et des pieds', price: 75, type: 'service' }
                ]
            },
            {
                user: {
                    email: 'resto.alpes@titelli.com',
                    password: 'Demo123!',
                    first_name: 'Pierre',
                    last_name: 'Blanc'
                },
                enterprise: {
                    business_name: 'Restaurant Les Alpes',
                    slogan: 'Cuisine suisse traditionnelle',
                    description: 'Restaurant gastronomique proposant une cuisine suisse authentique avec des produits locaux. Fondue, raclette et spécialités vaudoises.',
                    category: 'restauration',
                    address: 'Place de la Palud 5',
                    phone: '+41 21 456 78 90',
                    email: 'reservation@lesalpes.ch',
                    website: 'https://www.lesalpes.ch',
                    is_certified: true,
                    is_labeled: false,
                    is_premium: false,
                    rating: 4.5,
                    review_count: 42
                },
                services: [
                    { name: 'Menu dégustation', description: 'Menu 5 plats avec accord mets-vins', price: 89, type: 'service' },
                    { name: 'Fondue pour 2', description: 'Fondue moitié-moitié traditionnelle', price: 58, type: 'service' },
                    { name: 'Brunch dominical', description: 'Brunch complet le dimanche', price: 45, type: 'service' }
                ]
            },
            {
                user: {
                    email: 'sport.fitness@titelli.com',
                    password: 'Demo123!',
                    first_name: 'Marc',
                    last_name: 'Favre'
                },
                enterprise: {
                    business_name: 'FitPro Coaching',
                    slogan: 'Dépassez vos limites',
                    description: 'Coach sportif personnel et cours collectifs. Programmes personnalisés, nutrition et suivi de progression.',
                    category: 'cours_sport',
                    address: 'Avenue de la Gare 28',
                    phone: '+41 78 234 56 78',
                    email: 'contact@fitpro.ch',
                    website: null,
                    is_certified: false,
                    is_labeled: true,
                    is_premium: false,
                    rating: 4.9,
                    review_count: 18
                },
                services: [
                    { name: 'Coaching personnel', description: 'Séance individuelle de coaching sportif', price: 80, type: 'service' },
                    { name: 'Programme nutrition', description: 'Plan nutritionnel personnalisé sur 4 semaines', price: 150, type: 'service' },
                    { name: 'Cours collectif', description: 'Cours de fitness en groupe (10 séances)', price: 180, type: 'service' }
                ]
            },
            {
                user: {
                    email: 'mode.boutique@titelli.com',
                    password: 'Demo123!',
                    first_name: 'Claire',
                    last_name: 'Rochat'
                },
                enterprise: {
                    business_name: 'Boutique Élégance',
                    slogan: 'Mode éthique et tendance',
                    description: 'Boutique de mode proposant des vêtements éthiques et durables pour femmes. Collections exclusives de créateurs suisses.',
                    category: 'vetements_mode',
                    address: 'Rue de Bourg 18',
                    phone: '+41 21 567 89 01',
                    email: 'boutique@elegance.ch',
                    website: 'https://www.elegance-lausanne.ch',
                    is_certified: true,
                    is_labeled: true,
                    is_premium: true,
                    rating: 4.7,
                    review_count: 31
                },
                services: [
                    { name: 'Robe de soirée', description: 'Robe élégante pour vos événements', price: 289, type: 'product', is_delivery: true },
                    { name: 'Ensemble tailleur', description: 'Tailleur professionnel sur mesure', price: 450, type: 'product', is_delivery: true },
                    { name: 'Accessoires', description: 'Sac à main en cuir véritable', price: 175, type: 'product', is_delivery: true }
                ]
            },
            {
                user: {
                    email: 'coiffeur.studio@titelli.com',
                    password: 'Demo123!',
                    first_name: 'Thomas',
                    last_name: 'Müller'
                },
                enterprise: {
                    business_name: 'Studio Coiffure',
                    slogan: 'Votre style, notre passion',
                    description: 'Salon de coiffure moderne pour hommes et femmes. Coupes tendances, colorations et soins capillaires.',
                    category: 'coiffure_barber',
                    address: 'Avenue de Rumine 34',
                    phone: '+41 21 678 90 12',
                    email: 'rdv@studiocoiffure.ch',
                    website: null,
                    is_certified: false,
                    is_labeled: false,
                    is_premium: true,
                    rating: 4.6,
                    review_count: 56
                },
                services: [
                    { name: 'Coupe femme', description: 'Coupe, brushing et conseils personnalisés', price: 85, type: 'service' },
                    { name: 'Coupe homme', description: 'Coupe et stylisation', price: 45, type: 'service' },
                    { name: 'Coloration complète', description: 'Coloration avec soins', price: 120, type: 'service' }
                ]
            },
            {
                user: {
                    email: 'tech.repair@titelli.com',
                    password: 'Demo123!',
                    first_name: 'David',
                    last_name: 'Nkomo'
                },
                enterprise: {
                    business_name: 'TechFix Lausanne',
                    slogan: 'Réparation rapide et fiable',
                    description: 'Service de réparation pour smartphones, ordinateurs et tablettes. Diagnostic gratuit et garantie sur toutes les réparations.',
                    category: 'expert_tech',
                    address: 'Rue Centrale 7',
                    phone: '+41 79 345 67 89',
                    email: 'support@techfix.ch',
                    website: 'https://www.techfix-lausanne.ch',
                    is_certified: true,
                    is_labeled: false,
                    is_premium: false,
                    rating: 4.4,
                    review_count: 67
                },
                services: [
                    { name: 'Réparation écran iPhone', description: 'Remplacement écran avec pièces originales', price: 149, type: 'service' },
                    { name: 'Nettoyage PC', description: 'Nettoyage complet et optimisation', price: 79, type: 'service' },
                    { name: 'Récupération données', description: 'Récupération de données sur disque endommagé', price: 199, type: 'service' }
                ]
            }
        ];

        for (const data of enterprises) {
            // Create user
            const hashedPassword = await bcrypt.hash(data.user.password, 10);
            const userId = uuidv4();
            await db.collection('users').insertOne({
                id: userId,
                email: data.user.email,
                password: hashedPassword,
                first_name: data.user.first_name,
                last_name: data.user.last_name,
                phone: data.enterprise.phone,
                user_type: 'entreprise',
                cashback_balance: 0,
                is_premium: data.enterprise.is_premium,
                is_verified: true,
                is_certified: data.enterprise.is_certified,
                is_labeled: data.enterprise.is_labeled,
                city: 'Lausanne',
                created_at: new Date().toISOString()
            });

            // Create enterprise
            const enterpriseId = uuidv4();
            await db.collection('enterprises').insertOne({
                id: enterpriseId,
                user_id: userId,
                business_name: data.enterprise.business_name,
                slogan: data.enterprise.slogan,
                description: data.enterprise.description,
                category: data.enterprise.category,
                address: data.enterprise.address,
                city: 'Lausanne',
                phone: data.enterprise.phone,
                email: data.enterprise.email,
                website: data.enterprise.website,
                logo: null,
                cover_image: null,
                photos: [],
                videos: [],
                is_certified: data.enterprise.is_certified,
                is_labeled: data.enterprise.is_labeled,
                is_premium: data.enterprise.is_premium,
                rating: data.enterprise.rating,
                review_count: data.enterprise.review_count,
                created_at: new Date().toISOString()
            });

            // Create services/products
            for (const service of data.services) {
                await db.collection('services_products').insertOne({
                    id: uuidv4(),
                    enterprise_id: enterpriseId,
                    name: service.name,
                    description: service.description,
                    price: service.price,
                    currency: 'CHF',
                    category: data.enterprise.category,
                    type: service.type || 'service',
                    images: [],
                    is_available: true,
                    is_premium: data.enterprise.is_premium,
                    is_delivery: service.is_delivery || false,
                    created_at: new Date().toISOString()
                });
            }

            console.log(`   ✓ ${data.enterprise.business_name}`);
        }

        // Create sample reviews
        console.log('⭐ Création des avis...');
        const allEnterprises = await db.collection('enterprises').find().toArray();
        const reviewComments = [
            'Excellent service, je recommande vivement !',
            'Très professionnel et accueillant.',
            'Qualité au rendez-vous, j\'y retournerai.',
            'Bonne expérience dans l\'ensemble.',
            'Service impeccable et personnel très sympa.',
            'Un peu cher mais la qualité est là.',
            'Parfait, rien à redire !',
            'Très satisfait de ma visite.'
        ];

        for (const enterprise of allEnterprises.slice(0, 4)) {
            const numReviews = Math.floor(Math.random() * 3) + 2;
            for (let i = 0; i < numReviews; i++) {
                await db.collection('reviews').insertOne({
                    id: uuidv4(),
                    enterprise_id: enterprise.id,
                    user_id: clientId,
                    user_name: 'Marie Dupont',
                    rating: Math.floor(Math.random() * 2) + 4, // 4-5 stars
                    comment: reviewComments[Math.floor(Math.random() * reviewComments.length)],
                    created_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString()
                });
            }
        }

        // Create sample orders
        console.log('📦 Création des commandes...');
        const spaEnterprise = allEnterprises.find(e => e.business_name.includes('Spa'));
        if (spaEnterprise) {
            await db.collection('orders').insertOne({
                id: uuidv4(),
                user_id: clientId,
                enterprise_id: spaEnterprise.id,
                items: [
                    { name: 'Massage relaxant 60min', price: 120, quantity: 1 }
                ],
                total: 120,
                status: 'completed',
                payment_status: 'paid',
                delivery_address: null,
                notes: null,
                created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
            });
            
            await db.collection('orders').insertOne({
                id: uuidv4(),
                user_id: clientId,
                enterprise_id: spaEnterprise.id,
                items: [
                    { name: 'Soin visage premium', price: 95, quantity: 1 },
                    { name: 'Manucure & Pédicure', price: 75, quantity: 1 }
                ],
                total: 170,
                status: 'pending',
                payment_status: 'pending',
                delivery_address: null,
                notes: 'Rendez-vous à 14h',
                created_at: new Date().toISOString()
            });
        }

        console.log('\n✅ Base de données initialisée avec succès !');
        console.log('\n📋 Comptes de test :');
        console.log('   Admin    : admin@titelli.com / Admin123!');
        console.log('   Client   : test@example.com / Test123!');
        console.log('   Entreprise: spa.luxury@titelli.com / Demo123!');

    } catch (error) {
        console.error('❌ Erreur:', error);
    } finally {
        await client.close();
        process.exit(0);
    }
}

seedDatabase();
