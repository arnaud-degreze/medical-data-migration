#!/bin/bash

set -e

mongosh --quiet \
    --username "${MONGO_INITDB_ROOT_USERNAME}" \
    --password "${MONGO_INITDB_ROOT_PASSWORD}" \
    --authenticationDatabase admin \
    --eval "
        const database = db.getSiblingDB('medical');

        database.createUser({
            user: '${MONGO_MIGRATION_USERNAME}',
            pwd: '${MONGO_MIGRATION_PASSWORD}',
            roles: [{
                role: 'readWrite',
                db: 'medical'
            }],
            mechanisms: ['SCRAM-SHA-256'],
            passwordDigestor: 'server'
        });

        database.createUser({
            user: '${MONGO_ANALYST_USERNAME}',
            pwd: '${MONGO_ANALYST_PASSWORD}',
            roles: [{
                role: 'read',
                db: 'medical'
            }],
            mechanisms: ['SCRAM-SHA-256'],
            passwordDigestor: 'server'
        });
    "

