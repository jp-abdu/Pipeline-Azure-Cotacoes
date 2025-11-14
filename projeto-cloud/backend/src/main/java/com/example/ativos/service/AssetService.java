package com.example.ativos.service;
import com.example.ativos.model.Asset;
import com.example.ativos.repository.AssetRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import java.time.LocalDate;

@Service
public class AssetService {
  private final AssetRepository repo;
  public AssetService(AssetRepository repo) { this.repo = repo; }
  public Page<Asset> search(String nome, LocalDate from, LocalDate to, Pageable pageable) {
    return repo.search(nome, from, to, pageable);
  }
  public Asset findById(Long id) { return repo.findById(id).orElse(null); }
}
