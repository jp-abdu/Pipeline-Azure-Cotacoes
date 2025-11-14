package com.example.ativos.model;
import jakarta.persistence.*;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;

@Entity
@Table(name = "asset")
@Data
public class Asset {
  @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;
  private String nome;
  private BigDecimal volumeDiario;
  private BigDecimal precoFechamento;
  private BigDecimal precoAbertura;
  private LocalDate dataPregao;
  private BigDecimal precoMedio;
  // getters e setters
}
