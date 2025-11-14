package com.example.ativos.repository;
import com.example.ativos.model.Asset;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import java.time.LocalDate;

public interface AssetRepository extends JpaRepository<Asset, Long> {
@Query("SELECT a FROM Asset a WHERE (:nome IS NULL OR LOWER(a.nome) LIKE LOWER(CONCAT('%', :nome, '%'))) AND (:from IS NULL OR a.dataPregao >= :from)  AND (:to IS NULL OR a.dataPregao <= :to)")
  Page<Asset> search(@Param("nome") String nome, @Param("from") LocalDate from,
                     @Param("to") LocalDate to, Pageable pageable);
}
