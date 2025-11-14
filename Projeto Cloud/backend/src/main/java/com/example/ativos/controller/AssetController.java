package com.example.ativos.controller;
import com.example.ativos.model.Asset;
import com.example.ativos.service.AssetService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

@RestController
@RequestMapping("/api/assets")
@CrossOrigin(origins = "*")
public class AssetController {
  private final AssetService service;
  private final DateTimeFormatter fmt = DateTimeFormatter.ISO_DATE;

  public AssetController(AssetService service) { this.service = service; }

  @GetMapping
  public ResponseEntity<Page<Asset>> list(@RequestParam(required = false) String q,
                          @RequestParam(required = false) String from,
                          @RequestParam(required = false) String to,
                          @RequestParam(defaultValue = "0") int page,
                          @RequestParam(defaultValue = "30") int size) {
    LocalDate fromDate = from != null ? LocalDate.parse(from, fmt) : null;
    LocalDate toDate = to != null ? LocalDate.parse(to, fmt) : null;
    return ResponseEntity.ok(service.search(q, fromDate, toDate, PageRequest.of(page, size)));
  }

  @GetMapping("/{id}")
  public ResponseEntity<Asset> getById(@PathVariable Long id) { return ResponseEntity.ok(service.findById(id)); }
}
