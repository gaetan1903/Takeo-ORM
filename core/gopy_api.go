package core

import (
	"encoding/json"
	"fmt"
)

// TakeoAPI - Interface simplifiée pour les bindings gopy
// Évite les types complexes qui posent des problèmes avec gopy
type TakeoAPI struct {
	manager *TakeoManager
}

// NewTakeoAPI crée une nouvelle instance de l'API simplifiée
func NewTakeoAPI(host string, port int, user, password, database, sslmode string) (*TakeoAPI, error) {
	manager, err := NewTakeoManager(host, port, user, password, database, sslmode)
	if err != nil {
		return nil, err
	}
	
	return &TakeoAPI{
		manager: manager,
	}, nil
}

// RegisterEntity enregistre une entité (version simplifiée pour gopy)
func (api *TakeoAPI) RegisterEntity(name, tableName string, columnsJSON string, primaryKey string) error {
	// Parser le JSON pour récupérer les définitions de colonnes
	var columns map[string]string
	if err := json.Unmarshal([]byte(columnsJSON), &columns); err != nil {
		return fmt.Errorf("failed to parse columns JSON: %v", err)
	}
	
	return api.manager.RegisterEntity(name, tableName, columns, primaryKey)
}

// Save sauvegarde une entité (version simplifiée)
func (api *TakeoAPI) Save(entityType string, dataJSON string) (int64, error) {
	// Parser le JSON pour récupérer les données d'entité
	var entityData map[string]interface{}
	if err := json.Unmarshal([]byte(dataJSON), &entityData); err != nil {
		return 0, fmt.Errorf("failed to parse entity JSON: %v", err)
	}
	
	return api.manager.Save(entityType, entityData)
}

// SaveBatch sauvegarde plusieurs entités en batch (version optimisée)
func (api *TakeoAPI) SaveBatch(entityType string, entitiesJSON string) (string, error) {
	// Parser le JSON pour récupérer les données des entités
	var entitiesData []map[string]interface{}
	if err := json.Unmarshal([]byte(entitiesJSON), &entitiesData); err != nil {
		return "", fmt.Errorf("failed to parse entities JSON: %v", err)
	}
	
	ids, err := api.manager.SaveBatch(entityType, entitiesData)
	if err != nil {
		return "", err
	}
	
	// Retourner les IDs en JSON
	idsJSON, err := json.Marshal(ids)
	if err != nil {
		return "", fmt.Errorf("failed to marshal IDs: %v", err)
	}
	
	return string(idsJSON), nil
}

// FindByID trouve une entité par ID (retourne JSON string pour simplicité)
func (api *TakeoAPI) FindByID(entityType string, id int64) (string, error) {
	result, err := api.manager.FindByID(entityType, id)
	if err != nil {
		return "", err
	}
	
	// Marshaller le résultat en JSON
	jsonData, err := json.Marshal(result)
	if err != nil {
		return "", fmt.Errorf("failed to marshal result: %v", err)
	}
	return string(jsonData), nil
}

// FindAll trouve toutes les entités (retourne JSON string)
func (api *TakeoAPI) FindAll(entityType string) (string, error) {
	results, err := api.manager.FindAll(entityType)
	if err != nil {
		return "", err
	}
	
	// Marshaller les résultats en JSON
	jsonData, err := json.Marshal(results)
	if err != nil {
		return "", fmt.Errorf("failed to marshal results: %v", err)
	}
	return string(jsonData), nil
}

// Update met à jour une entité
func (api *TakeoAPI) Update(entityType string, id int64, updateJSON string) error {
	// Parser le JSON pour récupérer les mises à jour
	var updates map[string]interface{}
	if err := json.Unmarshal([]byte(updateJSON), &updates); err != nil {
		return fmt.Errorf("failed to parse update JSON: %v", err)
	}
	
	return api.manager.Update(entityType, id, updates)
}

// Delete supprime une entité
func (api *TakeoAPI) Delete(entityType string, id int64) error {
	return api.manager.Delete(entityType, id)
}

// CreateTable crée la table pour une entité
func (api *TakeoAPI) CreateTable(entityType string) error {
	return api.manager.CreateTable(entityType)
}

// DropTable supprime la table d'une entité
func (api *TakeoAPI) DropTable(entityType string) error {
	return api.manager.DropTable(entityType)
}

// Close ferme la connexion
func (api *TakeoAPI) Close() error {
	return api.manager.Close()
}

// Ping vérifie la connectivité
func (api *TakeoAPI) Ping() error {
	return api.manager.Ping()
}